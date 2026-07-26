import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from styles import load_css
from utils import load_data, page_header

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Sales Analytics",
    page_icon="📈",
    layout="wide"
)

load_css()

THEME = "plotly_white"

page_header(
    "Sales Analytics",
    "Business Intelligence Dashboard for Sales Performance"
)

# ==========================================
# LOAD DATA
# ==========================================

df = load_data()

# Ensure date is datetime
df["date"] = pd.to_datetime(df["date"])

# ==========================================
# FILTERS
# ==========================================

st.subheader("Filters")

f1, f2, f3, f4 = st.columns(4)

with f1:
    country = st.selectbox(
        "Country",
        ["All"] + sorted(df["country"].unique()),
        key="sales_country"
    )

with f2:
    category = st.selectbox(
        "Category",
        ["All"] + sorted(df["category"].unique()),
        key="sales_category"
    )

with f3:
    channel = st.selectbox(
        "Channel",
        ["All"] + sorted(df["channel"].unique()),
        key="sales_channel"
    )

with f4:
    year = st.selectbox(
        "Year",
        ["All"] + sorted(df["year"].unique()),
        key="sales_year"
    )
    
filtered = df.copy()

if country != "All":
    filtered = filtered[
        filtered["country"] == country
    ]

if category != "All":
    filtered = filtered[
        filtered["category"] == category
    ]

if channel != "All":
    filtered = filtered[
        filtered["channel"] == channel
    ]

if year != "All":
    filtered = filtered[
        filtered["year"] == year
    ]

if filtered.empty:
    st.warning("No data available.")
    st.stop()
    
# ==========================================================
# EXECUTIVE KPI SECTION
# ==========================================================

st.divider()

# ----------------------------------------------------------
# KPI Calculations
# ----------------------------------------------------------

total_revenue = filtered["net_sales"].sum()

gross_sales = filtered["gross_sales"].sum()

units_sold = filtered["units_sold"].sum()

average_selling_price = (
    total_revenue / units_sold
    if units_sold > 0 else 0
)

average_margin = filtered["margin_pct"].mean()

stockout_rate = (
    filtered["stock_out_flag"].mean() * 100
)

total_orders = len(filtered)

unique_products = filtered["sku_id"].nunique()

unique_stores = filtered["store_id"].nunique()

# ----------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric(
    "Revenue",
    f"${total_revenue:,.0f}"
)

k2.metric(
    "Gross Sales",
    f"${gross_sales:,.0f}"
)

k3.metric(
    "Units Sold",
    f"{units_sold:,.0f}"
)

k4.metric(
    "Avg Selling Price",
    f"${average_selling_price:,.2f}"
)

k5.metric(
    "Average Margin",
    f"{average_margin:.1f}%"
)

k6.metric(
    "Stockout Rate",
    f"{stockout_rate:.1f}%"
)

# ----------------------------------------------------------
# Secondary KPI Cards
# ----------------------------------------------------------

k7, k8, k9 = st.columns(3)

k7.metric(
    "Orders",
    f"{total_orders:,}"
)

k8.metric(
    "Products",
    f"{unique_products:,}"
)

k9.metric(
    "Stores",
    f"{unique_stores:,}"
)

# ==========================================================
# REVENUE PERFORMANCE
# ==========================================================

st.divider()

st.header("Revenue Performance")

# ----------------------------------------------------------
# Monthly Revenue
# ----------------------------------------------------------

revenue = filtered.copy()

revenue["date"] = pd.to_datetime(revenue["date"])

monthly_revenue = (
    revenue
    .groupby(pd.Grouper(key="date", freq="M"))
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .reset_index()
)

monthly_revenue["Moving Average"] = (
    monthly_revenue["Revenue"]
    .rolling(3)
    .mean()
)

# ----------------------------------------------------------
# Revenue Trend
# ----------------------------------------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=monthly_revenue["date"],
        y=monthly_revenue["Revenue"],
        mode="lines",
        name="Revenue",
        line=dict(width=3)
    )
)

fig.add_trace(
    go.Scatter(
        x=monthly_revenue["date"],
        y=monthly_revenue["Moving Average"],
        mode="lines",
        name="3-Month Average",
        line=dict(dash="dash")
    )
)

fig.update_layout(

    title="Monthly Revenue Trend",

    xaxis_title="Date",

    yaxis_title="Revenue ($)",

    hovermode="x unified",

    height=500,

    template=THEME,

    legend=dict(
        orientation="h",
        y=1.05
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Revenue Summary
# ----------------------------------------------------------

latest_month = monthly_revenue.iloc[-1]

highest_month = monthly_revenue.loc[
    monthly_revenue["Revenue"].idxmax()
]

lowest_month = monthly_revenue.loc[
    monthly_revenue["Revenue"].idxmin()
]

c1, c2, c3 = st.columns(3)

c1.metric(
    "Latest Month Revenue",
    f"${latest_month['Revenue']:,.0f}"
)

c2.metric(
    "Highest Revenue Month",
    f"${highest_month['Revenue']:,.0f}"
)

c3.metric(
    "Lowest Revenue Month",
    f"${lowest_month['Revenue']:,.0f}"
)

# ==========================================================
# GEOGRAPHICAL SALES ANALYSIS
# ==========================================================

st.divider()

st.header("Geographical Sales Analysis")

# ----------------------------------------------------------
# Revenue by Country
# ----------------------------------------------------------

country_sales = (
    filtered
    .groupby("country", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)


fig = px.bar(

    country_sales,

    x="country",

    y="Revenue",

    text="Revenue",

    title="Revenue Contribution by Country"

)


fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)


fig.update_layout(

    height=450,

    template=THEME,

    xaxis_title="Country",

    yaxis_title="Revenue ($)"

)


st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Country Ranking Table
# ----------------------------------------------------------

st.subheader("Country Performance Ranking")


country_table = country_sales.copy()

country_table["Revenue Share (%)"] = (
    country_table["Revenue"]
    /
    country_table["Revenue"].sum()
    *
    100
)


country_table["Revenue Share (%)"] = (
    country_table["Revenue Share (%)"]
    .round(2)
)


st.dataframe(

    country_table,

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# Geographic Sales Map
# ----------------------------------------------------------

st.subheader("Global Sales Distribution")


geo_sales = (
    filtered
    .groupby(
        [
            "country",
            "city",
            "latitude",
            "longitude"
        ],
        as_index=False
    )
    .agg(
        Revenue=("net_sales","sum"),
        Units=("units_sold","sum")
    )
)


fig = px.scatter_mapbox(

    geo_sales,

    lat="latitude",

    lon="longitude",

    size="Revenue",

    color="Revenue",

    hover_name="city",

    hover_data={
        "country":True,
        "Revenue":":$,.0f",
        "Units":":,.0f"
    },

    zoom=1,

    height=600

)


fig.update_layout(

    mapbox_style="open-street-map",

    template=THEME

)


st.plotly_chart(

    fig,

    use_container_width=True

)

# ----------------------------------------------------------
# Top Cities
# ----------------------------------------------------------

st.subheader("Top Performing Cities")


city_sales = (
    filtered
    .groupby(
        ["city","country"],
        as_index=False
    )
    .agg(
        Revenue=("net_sales","sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
    .head(10)
)


fig = px.bar(

    city_sales,

    x="Revenue",

    y="city",

    color="country",

    orientation="h",

    title="Top 10 Revenue Generating Cities"

)


fig.update_layout(

    height=500,

    template=THEME

)


st.plotly_chart(

    fig,

    use_container_width=True

)

# ==========================================================
# PRODUCT & CATEGORY PERFORMANCE
# ==========================================================

st.divider()

st.header("Product & Category Performance")

# ----------------------------------------------------------
# Top 10 Products
# ----------------------------------------------------------

left, right = st.columns(2)

top_products = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
    .head(10)
)

fig = px.bar(

    top_products,

    x="Revenue",

    y="sku_name",

    orientation="h",

    text="Revenue",

    color="Revenue",

    title="Top 10 Products by Revenue"

)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(

    height=500,

    template=THEME,

    yaxis_title="",

    xaxis_title="Revenue ($)"

)

left.plotly_chart(
    fig,
    use_container_width=True
)

bottom_products = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(
        Revenue=("net_sales", "sum")
    )
    .sort_values("Revenue")
    .head(10)
)

fig = px.bar(

    bottom_products,

    x="Revenue",

    y="sku_name",

    orientation="h",

    color="Revenue",

    title="Lowest Revenue Products"

)

fig.update_layout(

    height=500,

    template=THEME,

    yaxis_title="",

    xaxis_title="Revenue ($)"

)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Revenue by Category
# ----------------------------------------------------------

left, right = st.columns(2)

category_sales = (
    filtered
    .groupby("category", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig = px.bar(

    category_sales,

    x="category",

    y="Revenue",

    text="Revenue",

    color="Revenue",

    title="Revenue by Category"

)

fig.update_traces(

    texttemplate="$%{text:,.0f}",

    textposition="outside"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Category",

    yaxis_title="Revenue ($)"

)

left.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Revenue by Brand
# ----------------------------------------------------------

brand_sales = (
    filtered
    .groupby("brand", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig = px.bar(

    brand_sales,

    x="Revenue",

    y="brand",

    orientation="h",

    color="Revenue",

    title="Brand Performance"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Revenue ($)",

    yaxis_title=""

)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Category Contribution
# ----------------------------------------------------------

st.subheader("Category Revenue Contribution")

fig = px.pie(

    category_sales,

    names="category",

    values="Revenue",

    hole=0.55,

    title="Revenue Contribution by Category"

)

fig.update_layout(

    template=THEME,

    height=500,

    legend_title="Category"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Pareto Analysis
# ----------------------------------------------------------

st.subheader("Pareto Analysis (80/20 Rule)")

pareto = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(
        Revenue=("net_sales", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

pareto["Cumulative Revenue"] = pareto["Revenue"].cumsum()

pareto["Cumulative %"] = (
    pareto["Cumulative Revenue"]
    / pareto["Revenue"].sum()
    * 100
)

fig = go.Figure()

# Revenue bars
fig.add_trace(

    go.Bar(

        x=pareto["sku_name"],

        y=pareto["Revenue"],

        name="Revenue",

        marker_color="#1f77b4"

    )

)

# Cumulative percentage line
fig.add_trace(

    go.Scatter(

        x=pareto["sku_name"],

        y=pareto["Cumulative %"],

        mode="lines+markers",

        name="Cumulative %",

        yaxis="y2",

        line=dict(
            color="crimson",
            width=3
        )

    )

)

# 80% reference line
fig.add_hline(

    y=80,

    yref="y2",

    line_dash="dash",

    line_color="green",

    annotation_text="80%",

    annotation_position="top left"

)

fig.update_layout(

    title="Pareto Analysis of Product Revenue",

    template=THEME,

    height=600,

    xaxis=dict(
        title="Products",
        tickangle=-45
    ),

    yaxis=dict(
        title="Revenue ($)"
    ),

    yaxis2=dict(

        title="Cumulative Revenue %",

        overlaying="y",

        side="right",

        range=[0, 105]

    ),

    legend=dict(
        orientation="h"
    )

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Pareto Summary
# ----------------------------------------------------------

pareto_cutoff = (
    pareto["Cumulative %"] <= 80
).sum()

st.info(

    f"""
**Pareto Insight**

• Top **{pareto_cutoff}** products generate approximately **80%** of total revenue.

• Total Products: **{len(pareto)}**

• This helps identify the products that deserve the highest inventory and marketing priority.
"""
)

# ==========================================================
# EXECUTIVE PRODUCT INSIGHTS
# ==========================================================

st.divider()

st.subheader("Executive Product Insights")

best_product = top_products.iloc[0]
worst_product = bottom_products.iloc[0]
best_category = category_sales.iloc[0]
best_brand = brand_sales.iloc[0]

insights = []

# Top Product
insights.append(
    f"🏆 Highest revenue product is **{best_product['sku_name']}**, generating "
    f"**${best_product['Revenue']:,.0f}**."
)

# Lowest Product
insights.append(
    f"📉 Lowest revenue product is **{worst_product['sku_name']}**, generating only "
    f"**${worst_product['Revenue']:,.0f}**."
)

# Category Leader
insights.append(
    f"📦 Top-performing category is **{best_category['category']}**, contributing "
    f"**${best_category['Revenue']:,.0f}** in revenue."
)

# Brand Leader
insights.append(
    f"⭐ Leading brand is **{best_brand['brand']}**, generating "
    f"**${best_brand['Revenue']:,.0f}**."
)

# Pareto
if pareto_cutoff <= len(pareto) * 0.2:
    insights.append(
        "📊 Revenue follows the Pareto Principle: roughly 20% of products generate around 80% of total revenue."
    )
else:
    insights.append(
        "📊 Revenue is more evenly distributed across the product portfolio rather than concentrated in a few products."
    )

# Category Concentration
category_share = (
    best_category["Revenue"] /
    category_sales["Revenue"].sum()
) * 100

if category_share > 40:
    insights.append(
        f"⚠️ The **{best_category['category']}** category contributes **{category_share:.1f}%** of total revenue. Heavy dependence on one category increases business risk."
    )
else:
    insights.append(
        "✅ Revenue is reasonably diversified across product categories."
    )
    
for insight in insights:
    st.info(insight)
    
st.success(
    f"""
### Executive Summary

- Highest Revenue Product: **{best_product['sku_name']}**
- Best Performing Category: **{best_category['category']}**
- Leading Brand: **{best_brand['brand']}**
- Products Driving ~80% Revenue: **{pareto_cutoff}**
- Total Products Analysed: **{len(pareto)}**

**Recommendation:** Prioritize inventory availability and marketing investment for the highest-performing products while reviewing underperforming products for possible optimization or discontinuation.
"""
)

# ==========================================================
# SALES CHANNEL ANALYTICS
# ==========================================================

st.divider()

st.header("Sales Channel Analytics")

# ----------------------------------------------------------
# Revenue by Channel
# ----------------------------------------------------------

channel_sales = (
    filtered
    .groupby("channel", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        GrossSales=("gross_sales", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig = px.bar(

    channel_sales,

    x="channel",

    y="Revenue",

    text="Revenue",

    color="Revenue",

    title="Revenue by Sales Channel"

)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Sales Channel",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Units Sold by Channel")

fig = px.bar(

    channel_sales,

    x="channel",

    y="Units",

    text="Units",

    color="Units",

    title="Sales Volume"

)

fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Channel Revenue Contribution")

fig = px.pie(

    channel_sales,

    names="channel",

    values="Revenue",

    hole=0.55,

    title="Revenue Share by Channel"

)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Average Selling Price")

channel_sales["Average Price"] = (
    channel_sales["Revenue"]
    /
    channel_sales["Units"]
)

fig = px.bar(

    channel_sales,

    x="channel",

    y="Average Price",

    text="Average Price",

    color="Average Price",

    title="Average Selling Price by Channel"

)

fig.update_traces(
    texttemplate="$%{text:.2f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Average Margin by Channel")

channel_margin = (
    filtered
    .groupby("channel", as_index=False)
    .agg(
        Margin=("margin_pct", "mean")
    )
)

fig = px.bar(

    channel_margin,

    x="channel",

    y="Margin",

    text="Margin",

    color="Margin",

    title="Average Profit Margin"

)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    yaxis_title="Margin (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Executive Channel Insights")

best_channel = channel_sales.iloc[0]

highest_margin = (
    channel_margin
    .sort_values("Margin", ascending=False)
    .iloc[0]
)

largest_share = (
    best_channel["Revenue"]
    /
    channel_sales["Revenue"].sum()
    * 100
)

st.success(
    f"🏆 Highest revenue channel: **{best_channel['channel']}** "
    f"(${best_channel['Revenue']:,.0f})."
)

st.info(
    f"💰 Highest margin channel: **{highest_margin['channel']}** "
    f"({highest_margin['Margin']:.1f}% average margin)."
)

if largest_share > 50:

    st.warning(
        f"⚠️ {best_channel['channel']} contributes **{largest_share:.1f}%** of total revenue. "
        "The business is highly dependent on a single sales channel."
    )

else:

    st.success(
        "✅ Revenue is well distributed across multiple sales channels."
    )
# ==========================================================
# SEASONALITY & TIME INTELLIGENCE
# ==========================================================

st.divider()

st.header("Seasonality & Time Intelligence")

# ----------------------------------------------------------
# Build Time Intelligence Columns
# ----------------------------------------------------------

time_df = filtered.copy()

time_df["date"] = pd.to_datetime(time_df["date"])

time_df["year"] = time_df["date"].dt.year
time_df["month"] = time_df["date"].dt.month
time_df["month_name"] = time_df["date"].dt.strftime("%b")
time_df["quarter"] = "Q" + time_df["date"].dt.quarter.astype(str)
time_df["day_name"] = time_df["date"].dt.day_name()

# ----------------------------------------------------------
# 6.1 Monthly Revenue Trend
# ----------------------------------------------------------

monthly_sales = (
    time_df
    .groupby(["month", "month_name"], as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .sort_values("month")
)

fig = px.line(
    monthly_sales,
    x="month_name",
    y="Revenue",
    markers=True,
    title="Monthly Revenue Trend"
)

fig.update_traces(line=dict(width=4))

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Month",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------
# 6.2 Monthly Revenue Heatmap
# ----------------------------------------------------------

st.subheader("Monthly Revenue Heatmap")

heatmap_data = (
    time_df
    .pivot_table(
        values="net_sales",
        index="year",
        columns="month_name",
        aggfunc="sum"
    )
)

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

heatmap_data = heatmap_data.reindex(columns=month_order)

fig = px.imshow(
    heatmap_data,
    text_auto=".0f",
    color_continuous_scale="Blues",
    aspect="auto"
)

fig.update_layout(
    template=THEME,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------
# 6.3 Quarterly Revenue
# ----------------------------------------------------------

st.subheader("Quarterly Revenue")

quarter_sales = (
    time_df
    .groupby("quarter", as_index=False)
    .agg(
        Revenue=("net_sales", "sum")
    )
)

quarter_sales["quarter"] = pd.Categorical(
    quarter_sales["quarter"],
    categories=["Q1","Q2","Q3","Q4"],
    ordered=True
)

quarter_sales = quarter_sales.sort_values("quarter")

fig = px.bar(
    quarter_sales,
    x="quarter",
    y="Revenue",
    text="Revenue",
    color="Revenue",
    title="Revenue by Quarter"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Quarter",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------
# 6.4 Weekday Performance
# ----------------------------------------------------------

st.subheader("Sales by Weekday")

weekday_sales = (
    time_df
    .groupby("day_name", as_index=False)
    .agg(
        Revenue=("net_sales", "sum")
    )
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday_sales["day_name"] = pd.Categorical(
    weekday_sales["day_name"],
    categories=weekday_order,
    ordered=True
)

weekday_sales = weekday_sales.sort_values("day_name")

fig = px.bar(
    weekday_sales,
    x="day_name",
    y="Revenue",
    text="Revenue",
    color="Revenue",
    title="Revenue by Day of Week"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Day",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------
# 6.5 Holiday Performance
# ----------------------------------------------------------

st.subheader("Holiday Performance")

holiday_sales = (
    time_df
    .groupby("is_holiday", as_index=False)
    .agg(
        Revenue=("net_sales", "sum")
    )
)

holiday_sales["Period"] = holiday_sales["is_holiday"].map({
    0: "Non-Holiday",
    1: "Holiday"
})

fig = px.pie(
    holiday_sales,
    names="Period",
    values="Revenue",
    hole=0.5,
    title="Holiday Revenue Contribution"
)

fig.update_layout(
    template=THEME,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------
# 6.6 Weekend vs Weekday
# ----------------------------------------------------------

st.subheader("Weekend vs Weekday")

weekend_sales = (
    time_df
    .groupby("is_weekend", as_index=False)
    .agg(
        Revenue=("net_sales", "sum")
    )
)

weekend_sales["Type"] = weekend_sales["is_weekend"].map({
    0: "Weekday",
    1: "Weekend"
})

fig = px.bar(
    weekend_sales,
    x="Type",
    y="Revenue",
    text="Revenue",
    color="Revenue",
    title="Weekend Revenue"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------
# 6.7 Executive Time Insights
# ----------------------------------------------------------

st.subheader("Executive Time Insights")

best_month = monthly_sales.loc[
    monthly_sales["Revenue"].idxmax()
]

worst_month = monthly_sales.loc[
    monthly_sales["Revenue"].idxmin()
]

best_quarter = quarter_sales.loc[
    quarter_sales["Revenue"].idxmax()
]

best_day = weekday_sales.loc[
    weekday_sales["Revenue"].idxmax()
]

holiday_share = (
    holiday_sales.loc[
        holiday_sales["Period"] == "Holiday",
        "Revenue"
    ].sum()
    /
    holiday_sales["Revenue"].sum()
    * 100
)

st.success(
    f"Highest revenue month: **{best_month['month_name']}** "
    f"(${best_month['Revenue']:,.0f})."
)

st.info(
    f"Lowest revenue month: **{worst_month['month_name']}** "
    f"(${worst_month['Revenue']:,.0f})."
)

st.info(
    f"Best performing quarter: **{best_quarter['quarter']}** "
    f"(${best_quarter['Revenue']:,.0f})."
)

st.info(
    f"Highest sales day: **{best_day['day_name']}**."
)

if holiday_share > 20:
    st.warning(
        f"Holidays contribute **{holiday_share:.1f}%** of revenue, indicating strong seasonal demand."
    )
else:
    st.success(
        "Sales are relatively stable across holiday and non-holiday periods."
    )
    
# ==========================================================
# SECTION 7 — PROMOTION & PRICING ANALYTICS
# ==========================================================

st.divider()

st.header("Promotion & Pricing Analytics")

# ----------------------------------------------------------
# Prepare Pricing Data
# ----------------------------------------------------------

pricing_df = filtered.copy()

# Create effective selling price if it does not already exist
if "effective_price" not in pricing_df.columns:
    pricing_df["effective_price"] = (
        pricing_df["list_price"] *
        (1 - pricing_df["discount_pct"] / 100)
    )

# ==========================================================
# 7.1 PROMOTION VS NON-PROMOTION
# ==========================================================

st.subheader("Promotion vs Non-Promotion")

promotion_sales = (
    pricing_df
    .groupby("promo_flag", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
)

promotion_sales["Promotion"] = promotion_sales["promo_flag"].map({
    0: "No Promotion",
    1: "Promotion"
})

fig = px.bar(
    promotion_sales,
    x="Promotion",
    y="Revenue",
    text="Revenue",
    color="Promotion",
    title="Revenue Under Promotions"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 7.2 REVENUE BY DISCOUNT BAND
# ==========================================================

st.subheader("Revenue by Discount Band")

discount_bins = pd.cut(

    pricing_df["discount_pct"],

    bins=[0,5,10,20,30,40,50,100],

    labels=[
        "0-5%",
        "5-10%",
        "10-20%",
        "20-30%",
        "30-40%",
        "40-50%",
        "50%+"
    ],

    include_lowest=True

)

discount_sales = (
    pricing_df
    .assign(Discount_Band=discount_bins)
    .groupby("Discount_Band", observed=False, as_index=False)
    .agg(
        Revenue=("net_sales","sum")
    )
)

fig = px.bar(

    discount_sales,

    x="Discount_Band",

    y="Revenue",

    text="Revenue",

    color="Revenue",

    title="Revenue by Discount Band"

)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Discount Band",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 7.3 DISCOUNT IMPACT ON DEMAND
# ==========================================================

st.subheader("Discount Impact on Demand")

fig = px.scatter(

    pricing_df,

    x="discount_pct",

    y="units_sold",

    color="category",

    size="net_sales",

    opacity=0.70,

    title="Discount vs Units Sold"

)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 7.4 MARGIN VS DISCOUNT
# ==========================================================

st.subheader("Margin vs Discount")

fig = px.scatter(

    pricing_df,

    x="discount_pct",

    y="margin_pct",

    color="category",

    opacity=0.70,

    title="Margin Erosion from Discounts"

)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 7.5 PROMOTION UPLIFT
# ==========================================================

st.subheader("Promotion Uplift")

promo_avg = (
    pricing_df
    .groupby("promo_flag")
    .agg(
        Avg_Units=("units_sold","mean")
    )
)

promo_units = (
    promo_avg.loc[1,"Avg_Units"]
    if 1 in promo_avg.index
    else 0
)

normal_units = (
    promo_avg.loc[0,"Avg_Units"]
    if 0 in promo_avg.index
    else 0
)

uplift = (
    ((promo_units-normal_units)/normal_units)*100
    if normal_units > 0
    else 0
)

st.metric(
    "Promotion Uplift",
    f"{uplift:.1f}%"
)

# ==========================================================
# 7.6 AVERAGE SELLING PRICE BY CATEGORY
# ==========================================================

st.subheader("Average Selling Price by Category")

price_category = (
    pricing_df
    .groupby("category", as_index=False)
    .agg(
        Average_Price=("effective_price","mean")
    )
)

fig = px.bar(

    price_category,

    x="category",

    y="Average_Price",

    text="Average_Price",

    color="Average_Price",

    title="Average Selling Price"

)

fig.update_traces(
    texttemplate="$%{text:.2f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Category",
    yaxis_title="Average Price ($)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 7.7 EXECUTIVE PRICING INSIGHTS
# ==========================================================

st.subheader("Executive Pricing Insights")

highest_discount = pricing_df["discount_pct"].max()

avg_discount = pricing_df["discount_pct"].mean()

avg_margin = pricing_df["margin_pct"].mean()

st.success(
    f"Average discount across all sales is **{avg_discount:.1f}%**."
)

st.info(
    f"Maximum recorded discount is **{highest_discount:.1f}%**."
)

st.info(
    f"Average gross margin is **{avg_margin:.1f}%**."
)

if uplift > 10:

    st.success(
        f"Promotions increase average demand by **{uplift:.1f}%**, indicating strong campaign effectiveness."
    )

else:

    st.warning(
        "Promotions have limited impact on demand. Pricing strategy should be reviewed."
    )

if avg_margin < 20:

    st.error(
        "Margins are relatively low. Heavy discounting may be reducing profitability."
    )

elif avg_margin < 35:

    st.warning(
        "Margins are moderate. Monitor promotional campaigns closely."
    )

else:

    st.success(
        "Current pricing strategy maintains healthy profit margins."
    )
    
# ==========================================================
# SECTION 8 — INVENTORY & STOCK PERFORMANCE
# ==========================================================

st.divider()

st.header("Inventory & Stock Performance")

inventory_df = filtered.copy()

# ==========================================================
# 8.1 INVENTORY KPI CARDS
# ==========================================================

current_inventory = inventory_df["stock_on_hand"].sum()

average_inventory = inventory_df["stock_on_hand"].mean()

stockout_rate = inventory_df["stock_out_flag"].mean() * 100

average_lead_time = inventory_df["lead_time_days"].mean()

inventory_turnover = (
    inventory_df["net_sales"].sum()
    /
    max(average_inventory, 1)
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Current Inventory",
    f"{current_inventory:,.0f}"
)

k2.metric(
    "Average Stock",
    f"{average_inventory:,.1f}"
)

k3.metric(
    "Stockout Rate",
    f"{stockout_rate:.1f}%"
)

k4.metric(
    "Average Lead Time",
    f"{average_lead_time:.1f} Days"
)

k5.metric(
    "Inventory Turnover",
    f"{inventory_turnover:.2f}x"
)

# ==========================================================
# 8.2 INVENTORY BY CATEGORY
# ==========================================================

st.subheader("Inventory by Category")

inventory_category = (
    inventory_df
    .groupby("category", as_index=False)
    .agg(
        Stock=("stock_on_hand", "sum")
    )
    .sort_values(
        "Stock",
        ascending=False
    )
)

fig = px.bar(

    inventory_category,

    x="category",

    y="Stock",

    text="Stock",

    color="Stock",

    title="Inventory Distribution by Category"

)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Category",
    yaxis_title="Inventory Units"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.3 INVENTORY STATUS
# ==========================================================

st.subheader("Inventory Availability")

status = inventory_df.copy()

status["Inventory Status"] = np.where(
    status["stock_out_flag"] == 1,
    "Stock Out",
    "Available"
)

status_summary = (
    status
    .groupby("Inventory Status", as_index=False)
    .agg(
        Products=("sku_id", "count")
    )
)

fig = px.pie(

    status_summary,

    names="Inventory Status",

    values="Products",

    hole=0.55,

    title="Inventory Availability"

)

fig.update_layout(
    template=THEME,
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.4 LEAD TIME DISTRIBUTION
# ==========================================================

st.subheader("Supplier Lead Time Distribution")

fig = px.histogram(

    inventory_df,

    x="lead_time_days",

    nbins=20,

    title="Lead Time Distribution",

    color_discrete_sequence=["#1f77b4"]

)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Lead Time (Days)",
    yaxis_title="Number of Records"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.5 INVENTORY VS REVENUE
# ==========================================================

st.subheader("Inventory vs Revenue")

inventory_sales = (
    inventory_df
    .groupby("category", as_index=False)
    .agg(
        Stock=("stock_on_hand", "sum"),
        Revenue=("net_sales", "sum")
    )
)

fig = px.scatter(

    inventory_sales,

    x="Stock",

    y="Revenue",

    size="Revenue",

    color="category",

    text="category",

    title="Inventory versus Revenue"

)

fig.update_traces(
    textposition="top center"
)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.6 INVENTORY TURNOVER BY CATEGORY
# ==========================================================

st.subheader("Inventory Turnover by Category")

turnover = (
    inventory_df
    .groupby("category", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Inventory=("stock_on_hand", "mean")
    )
)

turnover["Inventory Turnover"] = (
    turnover["Revenue"]
    /
    turnover["Inventory"].replace(0, np.nan)
)

turnover = turnover.fillna(0)

fig = px.bar(

    turnover,

    x="category",

    y="Inventory Turnover",

    text="Inventory Turnover",

    color="Inventory Turnover",

    title="Inventory Turnover"

)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    yaxis_title="Turnover Ratio"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.7 TOP STOCKED PRODUCTS
# ==========================================================

st.subheader("Top 10 Products by Inventory")

top_inventory = (
    inventory_df
    .groupby("sku_name", as_index=False)
    .agg(
        Stock=("stock_on_hand", "sum")
    )
    .sort_values(
        "Stock",
        ascending=False
    )
    .head(10)
)

fig = px.bar(

    top_inventory,

    x="Stock",

    y="sku_name",

    orientation="h",

    color="Stock",

    title="Highest Inventory Products"

)

fig.update_layout(
    template=THEME,
    height=500,
    yaxis_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.8 STOCKOUTS BY CATEGORY
# ==========================================================

st.subheader("Stockout Rate by Category")

stockouts = (
    inventory_df
    .groupby("category", as_index=False)
    .agg(
        Stockout_Rate=("stock_out_flag", "mean")
    )
)

stockouts["Stockout_Rate"] *= 100

fig = px.bar(

    stockouts,

    x="category",

    y="Stockout_Rate",

    text="Stockout_Rate",

    color="Stockout_Rate",

    title="Stockout Rate by Category"

)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    yaxis_title="Stockout Rate (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# 8.9 EXECUTIVE INVENTORY INSIGHTS
# ==========================================================

st.subheader("Executive Inventory Insights")

highest_stock = top_inventory.iloc[0]

highest_turnover = turnover.loc[
    turnover["Inventory Turnover"].idxmax()
]

highest_stockout = stockouts.loc[
    stockouts["Stockout_Rate"].idxmax()
]

st.success(
    f"Highest stocked product is **{highest_stock['sku_name']}** "
    f"with **{highest_stock['Stock']:,.0f} units**."
)

st.info(
    f"Fastest moving category is **{highest_turnover['category']}** "
    f"with an inventory turnover of **{highest_turnover['Inventory Turnover']:.2f}x**."
)

st.info(
    f"Highest stockout category is **{highest_stockout['category']}** "
    f"({highest_stockout['Stockout_Rate']:.1f}% stockout rate)."
)

if stockout_rate > 10:

    st.error(
        f"Overall stockout rate is **{stockout_rate:.1f}%**, indicating inventory shortages."
    )

elif stockout_rate > 5:

    st.warning(
        f"Overall stockout rate is **{stockout_rate:.1f}%**. Inventory should be monitored."
    )

else:

    st.success(
        "Inventory availability is healthy with minimal stockouts."
    )

if average_lead_time > 14:

    st.warning(
        f"Average supplier lead time is **{average_lead_time:.1f} days**, increasing replenishment risk."
    )

else:

    st.success(
        "Supplier lead times are within acceptable operational limits."
    )
    
# ==========================================================
# EXECUTIVE SUMMARY DASHBOARD
# ==========================================================

st.divider()

st.header("Executive Summary Dashboard")

# ----------------------------------------------------------
# Executive KPI Summary
# ----------------------------------------------------------

st.subheader("Business Performance Summary")

summary1, summary2, summary3, summary4 = st.columns(4)

summary1.metric(
    "Total Revenue",
    f"${total_revenue:,.0f}"
)

summary2.metric(
    "Units Sold",
    f"{units_sold:,.0f}"
)

summary3.metric(
    "Products",
    f"{unique_products:,}"
)

summary4.metric(
    "Stores",
    f"{unique_stores:,}"
)

# ----------------------------------------------------------
# Executive Scorecards
# ----------------------------------------------------------

st.subheader("Performance Scorecard")

score1, score2, score3 = st.columns(3)

if average_margin >= 30:
    score1.success(f"Margin: {average_margin:.1f}%")
elif average_margin >= 20:
    score1.warning(f"Margin: {average_margin:.1f}%")
else:
    score1.error(f"Margin: {average_margin:.1f}%")

if stockout_rate <= 5:
    score2.success(f"Stockout Rate: {stockout_rate:.1f}%")
elif stockout_rate <= 10:
    score2.warning(f"Stockout Rate: {stockout_rate:.1f}%")
else:
    score2.error(f"Stockout Rate: {stockout_rate:.1f}%")

if average_selling_price >= filtered["net_sales"].mean() / max(filtered["units_sold"].mean(), 1):
    score3.success(f"Average Selling Price: ${average_selling_price:.2f}")
else:
    score3.info(f"Average Selling Price: ${average_selling_price:.2f}")

# ----------------------------------------------------------
# Best Performing Entities
# ----------------------------------------------------------

st.subheader("Top Business Performers")

best_country = (
    filtered
    .groupby("country", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
    .iloc[0]
)

best_city = (
    filtered
    .groupby("city", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
    .iloc[0]
)

best_product = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
    .iloc[0]
)

best_category = (
    filtered
    .groupby("category", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
    .iloc[0]
)

best_brand = (
    filtered
    .groupby("brand", as_index=False)
    .agg(Revenue=("net_sales", "sum"))
    .sort_values("Revenue", ascending=False)
    .iloc[0]
)

col1, col2 = st.columns(2)

with col1:

    st.success(
        f"""
**Top Country**

{best_country['country']}

Revenue: **${best_country['Revenue']:,.0f}**
"""
    )

    st.success(
        f"""
**Top City**

{best_city['city']}

Revenue: **${best_city['Revenue']:,.0f}**
"""
    )

with col2:

    st.success(
        f"""
**Top Product**

{best_product['sku_name']}

Revenue: **${best_product['Revenue']:,.0f}**
"""
    )

    st.success(
        f"""
**Top Category**

{best_category['category']}

Revenue: **${best_category['Revenue']:,.0f}**
"""
    )

st.info(
    f"""
**Leading Brand**

{best_brand['brand']}

Revenue: **${best_brand['Revenue']:,.0f}**
"""
)

# ----------------------------------------------------------
# Executive Recommendations
# ----------------------------------------------------------

st.subheader("Executive Recommendations")

recommendations = []

if stockout_rate > 10:
    recommendations.append(
        "High stockout rate detected. Increase inventory planning and replenishment frequency."
    )

if average_margin < 20:
    recommendations.append(
        "Profit margins are relatively low. Review pricing strategy and supplier costs."
    )

if filtered["discount_pct"].mean() > 20:
    recommendations.append(
        "Average discounts are high. Evaluate promotional effectiveness and profitability."
    )

if unique_products > 300:
    recommendations.append(
        "Large product portfolio detected. Consider SKU rationalisation to improve operational efficiency."
    )

if best_product["Revenue"] > total_revenue * 0.20:
    recommendations.append(
        "Revenue is concentrated in a few products. Reduce dependency by expanding high-performing product lines."
    )

if best_country["Revenue"] > total_revenue * 0.40:
    recommendations.append(
        "Revenue is concentrated in one country. Consider geographic expansion opportunities."
    )

if not recommendations:
    recommendations.append(
        "Business performance is balanced across major operational indicators."
    )

for rec in recommendations:
    st.info(rec)

# ----------------------------------------------------------
# Executive Summary Table
# ----------------------------------------------------------

st.subheader("Executive Summary Table")

summary_table = pd.DataFrame({

    "Metric": [

        "Revenue",

        "Gross Sales",

        "Units Sold",

        "Average Selling Price",

        "Average Margin",

        "Stockout Rate",

        "Products",

        "Stores",

        "Orders"

    ],

    "Value": [

        f"${total_revenue:,.0f}",

        f"${gross_sales:,.0f}",

        f"{units_sold:,.0f}",

        f"${average_selling_price:.2f}",

        f"{average_margin:.1f}%",

        f"{stockout_rate:.1f}%",

        unique_products,

        unique_stores,

        total_orders

    ]

})

st.dataframe(
    summary_table,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Download Executive Report
# ----------------------------------------------------------

st.subheader("Download Executive Report")

executive_report = pd.DataFrame({

    "Report Date": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")],

    "Revenue": [round(total_revenue)],

    "Gross Sales": [round(gross_sales)],

    "Units Sold": [round(units_sold)],

    "Average Selling Price": [round(average_selling_price, 2)],

    "Average Margin (%)": [round(average_margin, 2)],

    "Stockout Rate (%)": [round(stockout_rate, 2)],

    "Products": [unique_products],

    "Stores": [unique_stores],

    "Orders": [total_orders],

    "Top Country": [best_country["country"]],

    "Top City": [best_city["city"]],

    "Top Product": [best_product["sku_name"]],

    "Top Category": [best_category["category"]],

    "Top Brand": [best_brand["brand"]]

})

st.dataframe(
    executive_report,
    hide_index=True,
    use_container_width=True
)

csv = executive_report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Executive Summary",
    data=csv,
    file_name="executive_summary.csv",
    mime="text/csv",
    use_container_width=True
)

# ----------------------------------------------------------
# Dashboard Footer
# ----------------------------------------------------------

st.divider()

st.caption(
    f"""
Dashboard generated on {pd.Timestamp.now():%d %B %Y %H:%M}

FMCG Global Demand Forecasting & Analytics Platform
"""
)