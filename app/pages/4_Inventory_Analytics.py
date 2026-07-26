import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from styles import load_css
from utils import load_data, page_header

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Inventory Analytics",
    page_icon="📦",
    layout="wide"
)

load_css()

THEME = "plotly_white"

page_header(
    "📦 Inventory Analytics",
    "Inventory Monitoring, Stock Health and Replenishment Intelligence"
)

# ==========================================================
# LOAD DATA
# ==========================================================

df = load_data()

df["date"] = pd.to_datetime(df["date"])

# ==========================================================
# SECTION 1 — FILTERS
# ==========================================================

st.subheader("Filters")

f1, f2, f3 = st.columns(3)

with f1:

    country = st.selectbox(
        "Country",
        ["All"] + sorted(df["country"].unique()),
        key="inventory_country"
    )

with f2:

    category = st.selectbox(
        "Category",
        ["All"] + sorted(df["category"].unique()),
        key="inventory_category"
    )

with f3:

    brand = st.selectbox(
        "Brand",
        ["All"] + sorted(df["brand"].unique()),
        key="inventory_brand"
    )

f4, f5, f6 = st.columns(3)

with f4:

    store = st.selectbox(
        "Store",
        ["All"] + sorted(df["store_id"].unique()),
        key="inventory_store"
    )

with f5:

    channel = st.selectbox(
        "Channel",
        ["All"] + sorted(df["channel"].unique()),
        key="inventory_channel"
    )

with f6:

    year = st.selectbox(
        "Year",
        ["All"] + sorted(df["year"].unique()),
        key="inventory_year"
    )

# ==========================================================
# APPLY FILTERS
# ==========================================================

filtered = df.copy()

if country != "All":
    filtered = filtered[
        filtered["country"] == country
    ]

if category != "All":
    filtered = filtered[
        filtered["category"] == category
    ]

if brand != "All":
    filtered = filtered[
        filtered["brand"] == brand
    ]

if store != "All":
    filtered = filtered[
        filtered["store_id"] == store
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
    st.warning(
        "No inventory records available for the selected filters."
    )
    st.stop()

# ==========================================================
# SECTION 2 — INVENTORY KPI DASHBOARD
# ==========================================================

st.divider()

st.header("Inventory Overview")

# ----------------------------------------------------------
# KPI Calculations
# ----------------------------------------------------------

current_inventory = filtered["stock_on_hand"].sum()

inventory_value = (
    filtered["stock_on_hand"] *
    filtered["list_price"]
).sum()

average_inventory = (
    filtered["stock_on_hand"].mean()
)

inventory_turnover = (
    filtered["units_sold"].sum()
    /
    max(average_inventory, 1)
)

days_of_cover = (
    filtered["stock_on_hand"].sum()
    /
    max(filtered["units_sold"].mean(), 1)
)

stockout_rate = (
    filtered["stock_out_flag"].mean()
    * 100
)

average_lead_time = (
    filtered["lead_time_days"].mean()
)

active_products = (
    filtered["sku_id"].nunique()
)

active_stores = (
    filtered["store_id"].nunique()
)

inventory_accuracy = (
    100 - stockout_rate
)

# ----------------------------------------------------------
# Primary KPI Cards
# ----------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Current Inventory",
    f"{current_inventory:,.0f} Units"
)

k2.metric(
    "Inventory Value",
    f"${inventory_value:,.0f}"
)

k3.metric(
    "Inventory Turnover",
    f"{inventory_turnover:.2f}x"
)

k4.metric(
    "Days of Cover",
    f"{days_of_cover:.1f} Days"
)

# ----------------------------------------------------------
# Secondary KPI Cards
# ----------------------------------------------------------

k5, k6, k7, k8 = st.columns(4)

k5.metric(
    "Stockout Rate",
    f"{stockout_rate:.1f}%"
)

k6.metric(
    "Average Lead Time",
    f"{average_lead_time:.1f} Days"
)

k7.metric(
    "Active Products",
    f"{active_products:,}"
)

k8.metric(
    "Active Stores",
    f"{active_stores:,}"
)

# ----------------------------------------------------------
# Inventory Health Score
# ----------------------------------------------------------

health_score = 100

if stockout_rate > 10:
    health_score -= 25

if inventory_turnover < 2:
    health_score -= 20

if days_of_cover > 90:
    health_score -= 15

if average_lead_time > 14:
    health_score -= 10

health_score = max(0, min(100, health_score))

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=health_score,
        number={"suffix": "%"},
        title={"text": "Inventory Health Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [0, 50], "color": "#ffcccc"},
                {"range": [50, 80], "color": "#fff2cc"},
                {"range": [80, 100], "color": "#d9ead3"},
            ],
        },
    )
)

fig.update_layout(
    template=THEME,
    height=350
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Inventory Snapshot
# ----------------------------------------------------------

st.subheader("Executive Inventory Snapshot")

st.info(
    f"""
### Inventory Summary

- **Current Inventory:** {current_inventory:,.0f} units
- **Inventory Value:** ${inventory_value:,.0f}
- **Inventory Turnover:** {inventory_turnover:.2f}x
- **Days of Cover:** {days_of_cover:.1f} days
- **Stockout Rate:** {stockout_rate:.1f}%
- **Average Lead Time:** {average_lead_time:.1f} days
- **Inventory Health Score:** {health_score:.0f}%
"""
)

# ==========================================================
# SECTION 3 — INVENTORY DISTRIBUTION
# ==========================================================

st.divider()

st.header("Inventory Distribution")

# ----------------------------------------------------------
# Inventory by Category
# ----------------------------------------------------------

left, right = st.columns(2)

category_inventory = (
    filtered
    .groupby("category", as_index=False)
    .agg(
        Inventory=("stock_on_hand", "sum"),
        Inventory_Value=("list_price", "mean")
    )
)

category_inventory["Inventory Value"] = (
    category_inventory["Inventory"] *
    category_inventory["Inventory_Value"]
)

fig = px.bar(

    category_inventory,

    x="category",

    y="Inventory",

    text="Inventory",

    color="Inventory",

    title="Inventory by Category"

)

fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Category",
    yaxis_title="Units in Stock"
)

left.plotly_chart(
    fig,
    use_container_width=True
)

brand_inventory = (
    filtered
    .groupby("brand", as_index=False)
    .agg(
        Inventory=("stock_on_hand", "sum")
    )
    .sort_values(
        "Inventory",
        ascending=False
    )
)

fig = px.bar(

    brand_inventory,

    x="Inventory",

    y="brand",

    orientation="h",

    color="Inventory",

    title="Inventory by Brand"

)

fig.update_layout(
    template=THEME,
    height=450,
    yaxis_title=""
)

right.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Inventory Distribution by Country")

country_inventory = (
    filtered
    .groupby("country", as_index=False)
    .agg(
        Inventory=("stock_on_hand", "sum")
    )
    .sort_values(
        "Inventory",
        ascending=False
    )
)

fig = px.pie(

    country_inventory,

    names="country",

    values="Inventory",

    hole=0.55,

    title="Inventory Share by Country"

)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Top Stores by Inventory")

store_inventory = (
    filtered
    .groupby("store_id", as_index=False)
    .agg(
        Inventory=("stock_on_hand", "sum")
    )
    .sort_values(
        "Inventory",
        ascending=False
    )
    .head(15)
)

fig = px.bar(

    store_inventory,

    x="Inventory",

    y="store_id",

    orientation="h",

    color="Inventory",

    title="Top 15 Stores by Inventory"

)

fig.update_layout(
    template=THEME,
    height=550,
    yaxis_title="Store"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Inventory Map")

geo_inventory = (
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
        Inventory=("stock_on_hand", "sum")
    )
)

fig = px.scatter_mapbox(

    geo_inventory,

    lat="latitude",

    lon="longitude",

    size="Inventory",

    color="Inventory",

    hover_name="city",

    hover_data={
        "country": True,
        "Inventory": ":,.0f"
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

st.subheader("Executive Distribution Insights")

largest_category = category_inventory.loc[
    category_inventory["Inventory"].idxmax()
]

largest_brand = brand_inventory.iloc[0]

largest_country = country_inventory.iloc[0]

largest_store = store_inventory.iloc[0]

st.success(
    f"Highest inventory category: **{largest_category['category']}** "
    f"({largest_category['Inventory']:,.0f} units)."
)

st.info(
    f"Largest brand inventory: **{largest_brand['brand']}** "
    f"({largest_brand['Inventory']:,.0f} units)."
)

st.info(
    f"Country holding the largest inventory: **{largest_country['country']}** "
    f"({largest_country['Inventory']:,.0f} units)."
)

st.info(
    f"Highest inventory store: **{largest_store['store_id']}** "
    f"({largest_store['Inventory']:,.0f} units)."
)

# ==========================================================
# SECTION 4 — STOCK HEALTH ANALYSIS
# ==========================================================

st.divider()

st.header("Stock Health Analysis")

# ----------------------------------------------------------
# Inventory Coverage
# ----------------------------------------------------------

coverage = (
    filtered
    .groupby(
        [
            "sku_id",
            "sku_name"
        ],
        as_index=False
    )
    .agg(
        Stock=("stock_on_hand", "sum"),
        Demand=("units_sold", "mean")
    )
)

coverage["Coverage"] = (
    coverage["Stock"]
    /
    coverage["Demand"].clip(lower=1)
)

coverage["Coverage"] = (
    coverage["Coverage"]
    .round(2)
)

left, right = st.columns(2)

overstock = (
    coverage
    .sort_values(
        "Coverage",
        ascending=False
    )
    .head(10)
)

fig = px.bar(

    overstock,

    x="Coverage",

    y="sku_name",

    orientation="h",

    color="Coverage",

    title="Top Overstocked Products"

)

fig.update_layout(
    template=THEME,
    height=500,
    yaxis_title=""
)

left.plotly_chart(
    fig,
    use_container_width=True
)

understock = (
    coverage
    .sort_values("Coverage")
    .head(10)
)

fig = px.bar(

    understock,

    x="Coverage",

    y="sku_name",

    orientation="h",

    color="Coverage",

    title="Top Understocked Products"

)

fig.update_layout(
    template=THEME,
    height=500,
    yaxis_title=""
)

right.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Fast & Slow Moving Products")

movement = (
    filtered
    .groupby(
        "sku_name",
        as_index=False
    )
    .agg(
        Units=("units_sold", "sum")
    )
)

movement = movement.sort_values(
    "Units",
    ascending=False
)

fast = movement.head(10)

slow = movement.tail(10)

left, right = st.columns(2)

fig = px.bar(

    fast,

    x="Units",

    y="sku_name",

    orientation="h",

    color="Units",

    title="Fast Moving Products"

)

fig.update_layout(
    template=THEME,
    height=500
)

left.plotly_chart(
    fig,
    use_container_width=True
)

fig = px.bar(

    slow,

    x="Units",

    y="sku_name",

    orientation="h",

    color="Units",

    title="Slow Moving Products"

)

fig.update_layout(
    template=THEME,
    height=500
)

right.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("ABC Inventory Classification")

abc = (
    filtered
    .groupby(
        "sku_name",
        as_index=False
    )
    .agg(
        Revenue=("net_sales", "sum")
    )
)

abc = abc.sort_values(
    "Revenue",
    ascending=False
)

abc["CumRevenue"] = abc["Revenue"].cumsum()

abc["CumPct"] = (
    abc["CumRevenue"]
    /
    abc["Revenue"].sum()
)

abc["Class"] = np.select(

    [
        abc["CumPct"] <= 0.80,
        abc["CumPct"] <= 0.95
    ],

    [
        "A",
        "B"
    ],

    default="C"

)

summary = (
    abc
    .groupby(
        "Class",
        as_index=False
    )
    .size()
)

fig = px.pie(

    summary,

    names="Class",

    values="size",

    hole=0.55,

    title="ABC Inventory Classification"

)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Inventory Health Status")

status = coverage.copy()

status["Inventory Status"] = np.where(

    status["Coverage"] < 1,

    "Understock",

    np.where(

        status["Coverage"] > 3,

        "Overstock",

        "Healthy"

    )

)

st.dataframe(

    status,

    hide_index=True,

    use_container_width=True

)

st.subheader("Executive Stock Insights")

over_count = (status["Inventory Status"] == "Overstock").sum()

under_count = (status["Inventory Status"] == "Understock").sum()

healthy_count = (status["Inventory Status"] == "Healthy").sum()

top_fast = fast.iloc[0]

top_slow = slow.iloc[0]

st.success(
    f"Fastest moving product: **{top_fast['sku_name']}** ({top_fast['Units']:,.0f} units sold)."
)

st.info(
    f"Slowest moving product: **{top_slow['sku_name']}** ({top_slow['Units']:,.0f} units sold)."
)

st.warning(
    f"Products requiring replenishment: **{under_count}**"
)

st.warning(
    f"Potential overstocked products: **{over_count}**"
)

st.success(
    f"Healthy inventory products: **{healthy_count}**"
)

if under_count > over_count:

    st.error(
        "Inventory shortages are currently the dominant operational risk."
    )

elif over_count > under_count:

    st.warning(
        "Inventory excess is the dominant operational issue. Consider inventory optimization."
    )

else:

    st.info(
        "Inventory appears reasonably balanced across products."
    )
    
# ==========================================================
# INVENTORY TURNOVER & STOCK MOVEMENT
# ==========================================================

st.divider()

st.header("Inventory Turnover & Stock Movement")

# ----------------------------------------------------------
# Inventory Turnover by Category
# ----------------------------------------------------------

turnover = (
    filtered
    .groupby("category", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Inventory=("stock_on_hand", "mean")
    )
)

turnover["Inventory Turnover"] = (
    turnover["Revenue"] /
    turnover["Inventory"].replace(0, np.nan)
)

left, right = st.columns(2)

fig = px.bar(

    turnover,

    x="category",

    y="Inventory Turnover",

    color="Inventory Turnover",

    text="Inventory Turnover",

    title="Inventory Turnover by Category"

)

fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Category",
    yaxis_title="Turnover Ratio"
)

left.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Average Days of Inventory
# ----------------------------------------------------------

turnover["Days Inventory"] = (
    365 /
    turnover["Inventory Turnover"].replace(0, np.nan)
)

fig = px.bar(

    turnover,

    x="category",

    y="Days Inventory",

    color="Days Inventory",

    text="Days Inventory",

    title="Average Days Inventory Held"

)

fig.update_traces(
    texttemplate="%{text:.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Category",
    yaxis_title="Days"
)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Monthly Inventory Movement
# ----------------------------------------------------------

st.subheader("Monthly Inventory Movement")

inventory_trend = (
    filtered
    .groupby(pd.Grouper(key="date", freq="M"))
    .agg(
        Average_Stock=("stock_on_hand", "mean"),
        Demand=("units_sold", "sum")
    )
    .reset_index()
)

fig = go.Figure()

# Average Stock
fig.add_trace(
    go.Scatter(
        x=inventory_trend["date"],
        y=inventory_trend["Average_Stock"],
        mode="lines+markers",
        name="Average Stock"
    )
)

# Demand
fig.add_trace(
    go.Scatter(
        x=inventory_trend["date"],
        y=inventory_trend["Demand"],
        mode="lines+markers",
        name="Units Sold",
        yaxis="y2"
    )
)

fig.update_layout(
    title="Inventory vs Sales",
    template=THEME,
    height=500,

    yaxis=dict(
        title="Average Stock"
    ),

    yaxis2=dict(
        title="Units Sold",
        overlaying="y",
        side="right"
    ),

    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Stock Distribution
# ----------------------------------------------------------

st.subheader("Inventory Distribution")

fig = px.histogram(

    filtered,

    x="stock_on_hand",

    nbins=40,

    color_discrete_sequence=["steelblue"],

    title="Distribution of Inventory Levels"

)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Units in Stock",
    yaxis_title="Frequency"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Inventory Efficiency Matrix
# ----------------------------------------------------------

st.subheader("Inventory Efficiency Matrix")

efficiency = (
    filtered
    .groupby("category", as_index=False)
    .agg(
        Average_Stock=("stock_on_hand", "mean"),
        Revenue=("net_sales", "sum")
    )
)

fig = px.scatter(

    efficiency,

    x="Average_Stock",

    y="Revenue",

    color="category",

    size="Revenue",

    hover_name="category",

    title="Inventory Efficiency"

)

fig.update_layout(
    template=THEME,
    height=550
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Slow Moving Inventory
# ----------------------------------------------------------

st.subheader("Slow Moving Inventory")

slow = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(
        Stock=("stock_on_hand", "mean"),
        Sales=("units_sold", "sum")
    )
)

slow["Stock-to-Sales"] = (
    slow["Stock"] /
    slow["Sales"].replace(0, np.nan)
)

slow = slow.sort_values(
    "Stock-to-Sales",
    ascending=False
).head(15)

st.dataframe(
    slow,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------------------------
# Fast Moving Inventory
# ----------------------------------------------------------

st.subheader("Fast Moving Inventory")

fast = (
    filtered
    .groupby("sku_name", as_index=False)
    .agg(
        Stock=("stock_on_hand", "mean"),
        Sales=("units_sold", "sum")
    )
)

fast["Sales-to-Stock"] = (
    fast["Sales"] /
    fast["Stock"].replace(0, np.nan)
)

fast = fast.sort_values(
    "Sales-to-Stock",
    ascending=False
).head(15)

st.dataframe(
    fast,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------------------------------
# Executive Insights
# ----------------------------------------------------------

st.subheader("Executive Inventory Insights")

best_turnover = turnover.loc[
    turnover["Inventory Turnover"].idxmax()
]

worst_turnover = turnover.loc[
    turnover["Inventory Turnover"].idxmin()
]

highest_days = turnover.loc[
    turnover["Days Inventory"].idxmax()
]

lowest_days = turnover.loc[
    turnover["Days Inventory"].idxmin()
]

st.success(
    f"Highest inventory turnover: **{best_turnover['category']}** "
    f"({best_turnover['Inventory Turnover']:.2f}x)."
)

st.info(
    f"Lowest inventory turnover: **{worst_turnover['category']}** "
    f"({worst_turnover['Inventory Turnover']:.2f}x)."
)

st.warning(
    f"Longest inventory holding period: **{highest_days['category']}** "
    f"({highest_days['Days Inventory']:.0f} days)."
)

st.success(
    f"Fastest inventory movement: **{lowest_days['category']}** "
    f"({lowest_days['Days Inventory']:.0f} days)."
)

avg_turnover = turnover["Inventory Turnover"].mean()

if avg_turnover >= 8:
    st.success(
        "Overall inventory turnover is excellent."
    )
elif avg_turnover >= 5:
    st.info(
        "Inventory turnover is healthy."
    )
else:
    st.warning(
        "Inventory turnover is relatively low. Consider reducing excess stock."
    )
    
# ==========================================================
# SECTION 6 - SUPPLIER & LEAD TIME ANALYTICS
# ==========================================================

st.divider()

st.header("Supplier & Lead Time Analytics")

# ----------------------------------------------------------
# Supplier Performance
# ----------------------------------------------------------

supplier_perf = (
    filtered
    .groupby("supplier_id", as_index=False)
    .agg(
        Avg_Lead_Time=("lead_time_days", "mean"),
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
)

supplier_perf["Supplier"] = (
    "Supplier " + supplier_perf["supplier_id"].astype(str)
)

supplier_perf = supplier_perf.sort_values(
    "Avg_Lead_Time",
    ascending=False
)

fig = px.bar(
    supplier_perf,
    x="Supplier",
    y="Avg_Lead_Time",
    color="Revenue",
    text="Avg_Lead_Time",
    title="Average Lead Time by Supplier"
)

fig.update_traces(
    texttemplate="%{text:.1f} days",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=500,
    xaxis_title="Supplier",
    yaxis_title="Average Lead Time (Days)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Lead Time Distribution
# ----------------------------------------------------------

st.subheader("Lead Time Distribution")

fig = px.histogram(
    filtered,
    x="lead_time_days",
    nbins=20,
    color_discrete_sequence=["#1f77b4"],
    title="Distribution of Supplier Lead Times"
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

# ----------------------------------------------------------
# Products with Longest Lead Times
# ----------------------------------------------------------

st.subheader("Products with Longest Lead Times")

lead_products = (
    filtered
    .groupby(
        ["sku_name", "supplier_id"],
        as_index=False
    )
    .agg(
        Avg_Lead_Time=("lead_time_days", "mean"),
        Revenue=("net_sales", "sum")
    )
)

lead_products["Supplier"] = (
    "Supplier " + lead_products["supplier_id"].astype(str)
)

lead_products = lead_products.sort_values(
    "Avg_Lead_Time",
    ascending=False
).head(15)

fig = px.bar(
    lead_products,
    x="Avg_Lead_Time",
    y="sku_name",
    orientation="h",
    color="Revenue",
    hover_data=["Supplier"],
    title="Products Requiring the Longest Replenishment Time"
)

fig.update_layout(
    template=THEME,
    height=550,
    yaxis_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Supplier Revenue Contribution
# ----------------------------------------------------------

st.subheader("Supplier Revenue Contribution")

supplier_sales = (
    supplier_perf[
        ["Supplier", "Revenue"]
    ]
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig = px.pie(
    supplier_sales,
    names="Supplier",
    values="Revenue",
    hole=0.55,
    title="Revenue Contribution by Supplier"
)

fig.update_layout(
    template=THEME,
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Procurement Risk Matrix
# ----------------------------------------------------------

st.subheader("Procurement Risk Matrix")

risk = supplier_perf.copy()

fig = px.scatter(
    risk,
    x="Avg_Lead_Time",
    y="Revenue",
    size="Revenue",
    color="Avg_Lead_Time",
    hover_name="Supplier",
    title="Supplier Procurement Risk"
)

fig.update_layout(
    template=THEME,
    height=600,
    xaxis_title="Average Lead Time (Days)",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Supplier Performance Table
# ----------------------------------------------------------

st.subheader("Supplier Performance Table")

table = supplier_perf.copy()

table["Avg_Lead_Time"] = table["Avg_Lead_Time"].round(1)
table["Revenue"] = table["Revenue"].round(2)

table = table[
    [
        "Supplier",
        "Avg_Lead_Time",
        "Revenue",
        "Units"
    ]
]

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Procurement Insights
# ----------------------------------------------------------

st.subheader("Executive Procurement Insights")

best_supplier = supplier_perf.loc[
    supplier_perf["Avg_Lead_Time"].idxmin()
]

worst_supplier = supplier_perf.loc[
    supplier_perf["Avg_Lead_Time"].idxmax()
]

longest_product = lead_products.iloc[0]

avg_lead = supplier_perf["Avg_Lead_Time"].mean()

st.success(
    f"Fastest supplier: **{best_supplier['Supplier']}** "
    f"({best_supplier['Avg_Lead_Time']:.1f} days average lead time)."
)

st.warning(
    f"Slowest supplier: **{worst_supplier['Supplier']}** "
    f"({worst_supplier['Avg_Lead_Time']:.1f} days average lead time)."
)

st.info(
    f"Longest replenishment product: **{longest_product['sku_name']}** "
    f"supplied by **{longest_product['Supplier']}** "
    f"({longest_product['Avg_Lead_Time']:.1f} days)."
)

if avg_lead > 14:
    st.error(
        "Average supplier lead time exceeds two weeks. Consider reviewing procurement contracts or increasing safety stock."
    )
else:
    st.success(
        "Supplier lead times are generally within acceptable operational limits."
    )
    
# ==========================================================
# SECTION 7 - INVENTORY RISK & OPTIMIZATION
# ==========================================================

st.divider()

st.header("Inventory Risk & Optimization")

# ----------------------------------------------------------
# 7.1 Inventory Health Matrix
# ----------------------------------------------------------

st.subheader("Inventory Health Matrix")

inventory_health = (
    filtered
    .groupby(
        ["sku_name", "category"],
        as_index=False
    )
    .agg(
        Average_Stock=("stock_on_hand", "mean"),
        Demand=("units_sold", "sum"),
        Revenue=("net_sales", "sum")
    )
)

inventory_health["Stock Coverage"] = (
    inventory_health["Average_Stock"]
    /
    inventory_health["Demand"].replace(0, 1)
)

fig = px.scatter(

    inventory_health,

    x="Demand",

    y="Average_Stock",

    size="Revenue",

    color="Stock Coverage",

    hover_name="sku_name",

    title="Inventory Health Matrix"

)

fig.update_layout(

    template=THEME,

    height=600,

    xaxis_title="Demand",

    yaxis_title="Average Stock"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 7.2 Inventory Coverage Distribution
# ----------------------------------------------------------

st.subheader("Inventory Coverage")

coverage = inventory_health.copy()

fig = px.histogram(

    coverage,

    x="Stock Coverage",

    nbins=30,

    title="Distribution of Inventory Coverage"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Stock Coverage Ratio",

    yaxis_title="Products"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 7.3 Most Overstocked Products
# ----------------------------------------------------------

st.subheader("Most Overstocked Products")

overstock = (
    inventory_health
    .sort_values(
        "Stock Coverage",
        ascending=False
    )
    .head(15)
)

fig = px.bar(

    overstock,

    x="Stock Coverage",

    y="sku_name",

    orientation="h",

    color="Revenue",

    title="Highest Inventory Coverage"

)

fig.update_layout(

    template=THEME,

    height=550,

    yaxis_title=""

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 7.4 Most Understocked Products
# ----------------------------------------------------------

st.subheader("Most Understocked Products")

understock = (
    inventory_health
    .sort_values(
        "Stock Coverage"
    )
    .head(15)
)

fig = px.bar(

    understock,

    x="Stock Coverage",

    y="sku_name",

    orientation="h",

    color="Revenue",

    title="Lowest Inventory Coverage"

)

fig.update_layout(

    template=THEME,

    height=550,

    yaxis_title=""

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 7.5 Inventory Risk Classification
# ----------------------------------------------------------

st.subheader("Inventory Risk Classification")

risk = inventory_health.copy()

risk["Risk"] = pd.cut(

    risk["Stock Coverage"],

    bins=[0,0.5,1,2,100],

    labels=[

        "Critical",

        "High",

        "Normal",

        "Overstock"

    ]

)

risk_summary = (

    risk

    .groupby("Risk", observed=True)

    .size()

    .reset_index(name="Products")

)

fig = px.pie(

    risk_summary,

    names="Risk",

    values="Products",

    hole=0.55,

    title="Inventory Risk Distribution"

)

fig.update_layout(

    template=THEME,

    height=500

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 7.6 Inventory Optimization Opportunities
# ----------------------------------------------------------

st.subheader("Inventory Optimization Opportunities")

optimization = risk[
    risk["Risk"].isin(
        ["Critical", "Overstock"]
    )
].sort_values(
    "Revenue",
    ascending=False
)

st.dataframe(

    optimization[

        [

            "sku_name",

            "category",

            "Average_Stock",

            "Demand",

            "Stock Coverage",

            "Risk",

            "Revenue"

        ]

    ],

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# 7.7 Executive Inventory Insights
# ----------------------------------------------------------

st.subheader("Executive Inventory Insights")

critical = (risk["Risk"] == "Critical").sum()
high = (risk["Risk"] == "High").sum()
normal = (risk["Risk"] == "Normal").sum()
overstocked = (risk["Risk"] == "Overstock").sum()

st.metric(
    "Critical Products",
    critical
)

st.metric(
    "High Risk Products",
    high
)

st.metric(
    "Healthy Products",
    normal
)

st.metric(
    "Overstocked Products",
    overstocked
)

if critical > overstocked:

    st.error(
        "Inventory shortages pose a larger operational risk than excess inventory."
    )

elif overstocked > critical:

    st.warning(
        "Inventory carrying costs are likely higher than necessary because many products are overstocked."
    )

else:

    st.success(
        "Inventory levels are generally balanced across the product portfolio."
    )
    
# ==========================================================
# SECTION 8 - INVENTORY FORECASTING & REPLENISHMENT
# ==========================================================

st.divider()

st.header("Inventory Forecasting & Replenishment")

# ----------------------------------------------------------
# 8.1 Estimated Days of Inventory Remaining
# ----------------------------------------------------------

st.subheader("Estimated Days of Inventory Remaining")

forecast = (
    filtered
    .groupby(
        ["sku_name", "category"],
        as_index=False
    )
    .agg(
        Current_Stock=("stock_on_hand", "mean"),
        Daily_Demand=("units_sold", "mean"),
        Revenue=("net_sales", "sum")
    )
)

forecast["Days Remaining"] = (
    forecast["Current_Stock"]
    /
    forecast["Daily_Demand"].replace(0, 1)
)

fig = px.scatter(

    forecast,

    x="Daily_Demand",

    y="Current_Stock",

    size="Revenue",

    color="Days Remaining",

    hover_name="sku_name",

    title="Inventory Days Remaining"

)

fig.update_layout(
    template=THEME,
    height=600,
    xaxis_title="Average Daily Demand",
    yaxis_title="Average Stock"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 8.2 Products Requiring Immediate Replenishment
# ----------------------------------------------------------

st.subheader("Products Requiring Immediate Replenishment")

replenishment = forecast.copy()

replenishment["Recommended Order"] = np.where(
    replenishment["Days Remaining"] < 7,
    (
        replenishment["Daily_Demand"] * 30
        -
        replenishment["Current_Stock"]
    ).clip(lower=0),
    0
)

urgent = (
    replenishment
    .query("`Recommended Order` > 0")
    .sort_values(
        "Recommended Order",
        ascending=False
    )
)

st.dataframe(

    urgent[

        [

            "sku_name",

            "category",

            "Current_Stock",

            "Daily_Demand",

            "Days Remaining",

            "Recommended Order"

        ]

    ],

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# 8.3 Reorder Quantity Analysis
# ----------------------------------------------------------

st.subheader("Recommended Reorder Quantities")

top_orders = urgent.head(15)

fig = px.bar(

    top_orders,

    x="Recommended Order",

    y="sku_name",

    orientation="h",

    color="Recommended Order",

    title="Largest Recommended Replenishment Orders"

)

fig.update_layout(

    template=THEME,

    height=600,

    yaxis_title=""

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 8.4 Days Remaining Distribution
# ----------------------------------------------------------

st.subheader("Inventory Coverage Distribution")

fig = px.histogram(

    forecast,

    x="Days Remaining",

    nbins=30,

    title="Distribution of Remaining Inventory Days"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Days Remaining",

    yaxis_title="Products"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 8.5 Inventory Forecast Status
# ----------------------------------------------------------

st.subheader("Inventory Forecast Status")

forecast["Status"] = pd.cut(

    forecast["Days Remaining"],

    bins=[0,7,14,30,10000],

    labels=[

        "Urgent",

        "Monitor",

        "Healthy",

        "Excess"

    ]

)

status = (

    forecast

    .groupby("Status", observed=True)

    .size()

    .reset_index(name="Products")

)

fig = px.pie(

    status,

    names="Status",

    values="Products",

    hole=0.55,

    title="Forecast Inventory Status"

)

fig.update_layout(

    template=THEME,

    height=500

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# 8.6 Forecast Risk Table
# ----------------------------------------------------------

st.subheader("Forecast Risk Table")

forecast_table = forecast.copy()

forecast_table = forecast_table.sort_values(
    "Days Remaining"
)

st.dataframe(

    forecast_table[

        [

            "sku_name",

            "category",

            "Current_Stock",

            "Daily_Demand",

            "Days Remaining",

            "Status"

        ]

    ],

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# 8.7 Executive Replenishment Insights
# ----------------------------------------------------------

st.subheader("Executive Replenishment Insights")

urgent_products = (forecast["Status"] == "Urgent").sum()
healthy_products = (forecast["Status"] == "Healthy").sum()
excess_products = (forecast["Status"] == "Excess").sum()

avg_days = forecast["Days Remaining"].mean()

st.metric(
    "Average Inventory Coverage",
    f"{avg_days:.1f} Days"
)

st.metric(
    "Urgent Products",
    urgent_products
)

st.metric(
    "Healthy Products",
    healthy_products
)

st.metric(
    "Excess Inventory",
    excess_products
)

if urgent_products > 0:

    st.error(
        f"{urgent_products} products require immediate replenishment to reduce stockout risk."
    )

if excess_products > 0:

    st.warning(
        f"{excess_products} products hold excess inventory that could increase carrying costs."
    )

if urgent_products == 0 and excess_products == 0:

    st.success(
        "Current inventory levels are well balanced across the product portfolio."
    )