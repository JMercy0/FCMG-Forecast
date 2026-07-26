import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from styles import load_css
from utils import load_data, page_header

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide"
)

load_css()

THEME = "plotly_white"

df = load_data()

page_header(
    "📊 Executive Dashboard",
    "Interactive Business Intelligence for FMCG Sales"
)

# ---------------------------------------------------
# Dashboard Filters
# ---------------------------------------------------

st.subheader("Dashboard Filters")

row1 = st.columns(3)

with row1[0]:
    country = st.selectbox(
        "Country",
        ["All"] + sorted(df["country"].unique()),
        key="country"
    )

with row1[1]:
    category = st.selectbox(
        "Category",
        ["All"] + sorted(df["category"].unique()),
        key="category"
    )

with row1[2]:
    channel = st.selectbox(
        "Channel",
        ["All"] + sorted(df["channel"].unique()),
        key="channel"
    )

row2 = st.columns(3)

with row2[0]:
    brand = st.selectbox(
        "Brand",
        ["All"] + sorted(df["brand"].unique()),
        key="brand"
    )

with row2[1]:
    if country == "All":
        cities = sorted(df["city"].unique())
    else:
        cities = sorted(df[df["country"] == country]["city"].unique())

    city = st.selectbox(
        "City",
        ["All"] + cities,
        key="city"
    )

with row2[2]:
    start_date, end_date = st.date_input(
        "Date Range",
        value=(df["date"].min(), df["date"].max())
    )

# ---------------------------------------------------
# Apply Filters
# ---------------------------------------------------

def apply_filters(data, country, city, category, channel, brand, start_date, end_date):
    """Apply all sidebar filter selections to the raw dataframe."""
    result = data.copy()

    if country != "All":
        result = result[result["country"] == country]

    if city != "All":
        result = result[result["city"] == city]

    if category != "All":
        result = result[result["category"] == category]

    if channel != "All":
        result = result[result["channel"] == channel]

    if brand != "All":
        result = result[result["brand"] == brand]

    result = result[
        (result["date"] >= pd.to_datetime(start_date)) &
        (result["date"] <= pd.to_datetime(end_date))
    ]

    return result


filtered = apply_filters(df, country, city, category, channel, brand, start_date, end_date)

# ---------------------------------------------------
# Empty Dataset Check
# ---------------------------------------------------

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------------------------------------------------
# KPI Cards
# ---------------------------------------------------

total_revenue = filtered["net_sales"].sum()
total_units = filtered["units_sold"].sum()
average_demand = filtered["units_sold"].mean()
active_products = filtered["sku_id"].nunique()
active_stores = filtered["store_id"].nunique()
stockouts = filtered["stock_out_flag"].sum()
average_margin = filtered["margin_pct"].mean()
total_inventory = filtered["stock_on_hand"].sum()
average_discount = filtered["discount_pct"].mean()

st.divider()
st.subheader("Executive KPIs")

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Revenue", f"${total_revenue:,.0f}")
k2.metric("📦 Units Sold", f"{total_units:,.0f}")
k3.metric("🏪 Stores", active_stores)
k4.metric("🛒 Products", active_products)

k5, k6, k7, k8 = st.columns(4)
k5.metric("📈 Avg Demand", f"{average_demand:.1f}")
k6.metric("📉 Avg Margin", f"{average_margin:.1f}%")
k7.metric("📦 Inventory", f"{total_inventory:,.0f}")
k8.metric("⚠ Stockouts", int(stockouts))

# ---------------------------------------------------
# KPI Trends
# ---------------------------------------------------

trend = (
    filtered
    .groupby(pd.Grouper(key="date", freq="ME"))
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
)

if len(trend) >= 2:
    previous_revenue = trend.iloc[-2]["Revenue"]
    previous_units = trend.iloc[-2]["Units"]

    if previous_revenue != 0:
        revenue_change = (
            (trend.iloc[-1]["Revenue"] - previous_revenue) / previous_revenue
        ) * 100
    else:
        revenue_change = 0

    if previous_units != 0:
        units_change = (
            (trend.iloc[-1]["Units"] - previous_units) / previous_units
        ) * 100
    else:
        units_change = 0

    c1, c2 = st.columns(2)
    c1.metric("Revenue Growth", f"{revenue_change:.2f}%", delta=f"{revenue_change:.2f}%")
    c2.metric("Demand Growth", f"{units_change:.2f}%", delta=f"{units_change:.2f}%")

# =====================================================
# SALES ANALYTICS
# =====================================================

st.divider()
st.subheader("📈 Sales Analytics")

left, right = st.columns(2)

# --- Monthly Revenue Trend ---

monthly = (
    filtered
    .groupby(pd.Grouper(key="date", freq="ME"))
    .agg(Revenue=("net_sales", "sum"))
    .reset_index()
)

monthly["Rolling Average"] = monthly["Revenue"].rolling(3).mean()

fig = px.line(
    monthly,
    x="date",
    y=["Revenue", "Rolling Average"],
    markers=True,
    title="Monthly Revenue Trend"
)

fig.update_layout(
    legend_title="",
    xaxis_title="Month",
    yaxis_title="Revenue ($)",
    hovermode="x unified",
    template=THEME
)

left.plotly_chart(fig, use_container_width=True)

# --- Revenue by Country ---

country_sales = (
    filtered
    .groupby("country", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
)

fig = px.bar(
    country_sales,
    x="Revenue",
    y="country",
    orientation="h",
    text_auto=".2s",
    title="Revenue by Country"
)

fig.update_layout(
    yaxis_title="",
    xaxis_title="Revenue ($)",
    template=THEME
)

right.plotly_chart(fig, use_container_width=True)

# --- Category / Channel ---

left, right = st.columns(2)

category_sales = (
    filtered
    .groupby(["category", "brand"], as_index=False)
    .agg(Revenue=("net_sales", "sum"))
)

fig = px.treemap(
    category_sales,
    path=["category", "brand"],
    values="Revenue",
    color="Revenue",
    title="Revenue by Category"
)

fig.update_layout(template=THEME)

left.plotly_chart(fig, use_container_width=True)

channel_sales = (
    filtered
    .groupby("channel", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
)

fig = px.bar(
    channel_sales,
    x="Revenue",
    y="channel",
    orientation="h",
    color="Revenue",
    text_auto=".2s",
    title="Sales Channel Performance"
)

fig.update_layout(
    template=THEME,
    xaxis_title="Revenue ($)",
    yaxis_title=""
)

right.plotly_chart(fig, use_container_width=True)

# =====================================================
# GEOGRAPHIC INTELLIGENCE
# =====================================================

st.divider()
st.subheader("🌍 Geographic Intelligence")

left, right = st.columns([2, 1])

city_sales = (
    filtered
    .groupby(["country", "city", "latitude", "longitude"], as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        Stockouts=("stock_out_flag", "sum")
    )
)

fig = px.scatter_map(
    city_sales,
    lat="latitude",
    lon="longitude",
    size="Revenue",
    color="Revenue",
    hover_name="city",
    hover_data={
        "country": True,
        "Revenue": ":,.0f",
        "Units": ":,.0f",
        "Stockouts": True
    },
    zoom=1,
    height=600,
    map_style="carto-positron",
    title="Revenue Distribution Across Cities"
)

fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))

left.plotly_chart(fig, use_container_width=True)

country_summary = (
    city_sales
    .groupby("country")
    .agg(Revenue=("Revenue", "sum"), Units=("Units", "sum"))
    .sort_values("Revenue", ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    country_summary,
    x="Revenue",
    y="country",
    orientation="h",
    text_auto=".2s",
    color="Revenue",
    title="Top Revenue Countries"
)

fig.update_layout(yaxis_title="", template=THEME)

right.plotly_chart(fig, use_container_width=True)

# =====================================================
# INVENTORY INTELLIGENCE
# =====================================================

st.divider()
st.subheader("📦 Inventory Intelligence")

left, right = st.columns(2)

inventory_by_category = (
    filtered
    .groupby("category", as_index=False)
    .agg(Stock=("stock_on_hand", "sum"), Revenue=("net_sales", "sum"))
)

fig = px.bar(
    inventory_by_category,
    x="category",
    y="Stock",
    color="Revenue",
    text_auto=".2s",
    title="Inventory by Category"
)

fig.update_layout(
    template=THEME,
    xaxis_title="Category",
    yaxis_title="Stock on Hand"
)

left.plotly_chart(fig, use_container_width=True)

fig = px.histogram(
    filtered,
    x="lead_time_days",
    nbins=20,
    title="Lead Time Distribution"
)

fig.update_layout(
    template=THEME,
    xaxis_title="Lead Time (Days)",
    yaxis_title="Number of Orders"
)

right.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

stockout_by_category = (
    filtered
    .groupby("category", as_index=False)
    .agg(Stockouts=("stock_out_flag", "sum"))
    .sort_values("Stockouts", ascending=False)
)

fig = px.bar(
    stockout_by_category,
    x="Stockouts",
    y="category",
    orientation="h",
    color="Stockouts",
    text_auto=True,
    title="Stockout Events by Category"
)

fig.update_layout(template=THEME, yaxis_title="")

left.plotly_chart(fig, use_container_width=True)

total_units_sold = filtered["units_sold"].sum()

if total_units_sold != 0:
    inventory_days = (filtered["stock_on_hand"].sum() / total_units_sold) * 30
else:
    inventory_days = 0

inventory_health = min(inventory_days, 100)

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=inventory_health,
        title={"text": "Inventory Health"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "royalblue"},
            "steps": [
                {"range": [0, 30], "color": "red"},
                {"range": [30, 70], "color": "orange"},
                {"range": [70, 100], "color": "green"}
            ]
        }
    )
)

fig.update_layout(height=450)

right.plotly_chart(fig, use_container_width=True)

# =====================================================
# PRODUCT PERFORMANCE
# =====================================================

st.divider()
st.subheader("🏆 Product Performance")

left, right = st.columns(2)

top_products = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(Revenue=("net_sales", "sum"), Units=("units_sold", "sum"))
    .sort_values("Revenue", ascending=False)
    .head(10)
)

fig = px.bar(
    top_products,
    x="Revenue",
    y="sku_name",
    orientation="h",
    text_auto=".2s",
    title="Top 10 Products by Revenue"
)

fig.update_layout(template=THEME, yaxis_title="")

left.plotly_chart(fig, use_container_width=True)

brand_sales = (
    filtered
    .groupby("brand", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
)

fig = px.bar(
    brand_sales,
    x="Revenue",
    y="brand",
    orientation="h",
    color="Revenue",
    text_auto=".2s",
    title="Brand Performance"
)

fig.update_layout(template=THEME)

right.plotly_chart(fig, use_container_width=True)

# =====================================================
# AI ANALYTICS
# =====================================================

st.divider()
st.subheader("🤖 AI Analytics")

monthly_units = (
    filtered
    .groupby(pd.Grouper(key="date", freq="ME"))
    .agg(Units=("units_sold", "sum"))
    .reset_index()
)

if len(monthly_units) >= 3:
    x = np.arange(len(monthly_units))
    y = monthly_units["Units"].values

    # Simple linear trend model: units ~ time
    slope, intercept = np.polyfit(x, y, 1)
    forecast_next = slope * len(monthly_units) + intercept
    forecast_next = max(forecast_next, 0)

    predicted = slope * x + intercept
    ss_res = np.sum((y - predicted) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    if r_squared >= 0.6:
        confidence_label = "High"
    elif r_squared >= 0.3:
        confidence_label = "Moderate"
    else:
        confidence_label = "Low"

    daily_forecast = forecast_next / 30

    if inventory_days < 10:
        suggested_action = "Increase inventory to cover rising demand."
    elif slope < 0 and inventory_days > 20:
        suggested_action = "Demand is softening — consider reducing next restock."
    else:
        suggested_action = "Maintain current inventory plan."

    ai1, ai2, ai3, ai4 = st.columns(4)
    ai1.metric("📈 Trend Direction", "Growing" if slope > 0 else "Declining")
    ai2.metric("🔮 Next Month Forecast", f"{forecast_next:,.0f} units")
    ai3.metric("📊 Model Fit (R²)", f"{r_squared:.2f}")
    ai4.metric("🎯 Confidence", confidence_label)

    forecast_chart = monthly_units.copy()
    forecast_row = pd.DataFrame({
        "date": [monthly_units["date"].max() + pd.DateOffset(months=1)],
        "Units": [forecast_next]
    })
    forecast_chart["Type"] = "Actual"
    forecast_row["Type"] = "Forecast"
    forecast_chart = pd.concat([forecast_chart, forecast_row], ignore_index=True)

    fig = px.line(
        forecast_chart,
        x="date",
        y="Units",
        color="Type",
        markers=True,
        title="Demand Trend & Next-Month Forecast (Linear Model)"
    )
    fig.update_layout(template=THEME, xaxis_title="Month", yaxis_title="Units Sold")

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"🧠 **AI Forecast Summary** — Model: Linear Trend Regression | "
        f"Expected demand: **{daily_forecast:.1f} units/day** | "
        f"Confidence: **{confidence_label}** | "
        f"Suggested action: **{suggested_action}**"
    )
else:
    st.warning("Not enough monthly history in the current filter selection to build a forecast (need at least 3 months).")

# =====================================================
# EXECUTIVE INSIGHTS & BUSINESS ALERTS
# =====================================================

st.divider()
st.subheader("🧠 Executive Insights")

insight_col1, insight_col2 = st.columns(2)

# --- Revenue Summary ---

best_country = filtered.groupby("country")["net_sales"].sum().idxmax()
country_revenue = filtered.groupby("country")["net_sales"].sum().max()

with insight_col1:
    st.success(f"💰 Total revenue generated is ${total_revenue:,.0f}.")
    st.info(
        f"🌍 Highest revenue comes from **{best_country}** (${country_revenue:,.0f})."
    )

# --- Best Performing Category ---

best_category = filtered.groupby("category")["net_sales"].sum().idxmax()
category_revenue = filtered.groupby("category")["net_sales"].sum().max()

with insight_col2:
    st.info(
        f"🏷 Best performing category is **{best_category}** (${category_revenue:,.0f})."
    )

# --- Promotion Effectiveness ---

if "promo_flag" in filtered.columns:
    promo = filtered.groupby("promo_flag")["net_sales"].mean()

    if len(promo) == 2:
        with insight_col1:
            if promo.loc[1] > promo.loc[0]:
                uplift = ((promo.loc[1] - promo.loc[0]) / promo.loc[0]) * 100
                st.success(f"🎯 Promotions increased average revenue by {uplift:.1f}%.")
            else:
                st.warning("🎯 Promotions are not generating higher sales.")

# --- Inventory Alert ---

with insight_col2:
    if stockouts > 0:
        st.error(f"⚠ {stockouts:,} stockout events detected.")
    else:
        st.success("✅ No stockouts detected.")

# --- Lead Time ---

avg_lead = filtered["lead_time_days"].mean()

with insight_col1:
    if avg_lead > 10:
        st.warning(f"🚚 Average supplier lead time is {avg_lead:.1f} days.")
    else:
        st.success(f"🚚 Average supplier lead time is {avg_lead:.1f} days.")

# --- Weather Insight ---

if "temperature" in filtered.columns:
    corr = filtered["temperature"].corr(filtered["units_sold"])

    with insight_col2:
        if corr > 0.4:
            st.info("🌞 Demand increases with higher temperatures.")
        elif corr < -0.4:
            st.info("❄ Demand decreases as temperature rises.")
        else:
            st.info("🌦 Temperature has limited influence on demand.")

# --- Inventory Recommendation ---

inventory_cover = inventory_days

with insight_col1:
    if inventory_cover < 5:
        st.error("📦 Inventory is critically low.")
    elif inventory_cover < 10:
        st.warning("📦 Inventory should be replenished soon.")
    else:
        st.success("📦 Inventory levels are healthy.")

# =====================================================
# TOP PRODUCTS TABLE
# =====================================================

st.divider()
st.subheader("🏆 Top Products")

top_products_table = (
    filtered
    .groupby("sku_name")
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        Margin=("margin_pct", "mean")
    )
    .sort_values("Revenue", ascending=False)
    .head(10)
)

st.dataframe(top_products_table, use_container_width=True)

# =====================================================
# DOWNLOAD FILTERED DATA
# =====================================================

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Filtered Data",
    csv,
    file_name="filtered_sales.csv",
    mime="text/csv"
)