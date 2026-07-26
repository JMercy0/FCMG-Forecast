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
    page_title="Customer & Market Analytics",
    page_icon="🌍",
    layout="wide"
)

load_css()

THEME = "plotly_white"

page_header(
    "🌍 Customer & Market Analytics",
    "Business Intelligence Dashboard for Market Performance, Customer Behaviour and Growth Opportunities."
)

# ==========================================================
# LOAD DATA
# ==========================================================

df = load_data()

# Ensure date column is datetime
df["date"] = pd.to_datetime(df["date"])

# ==========================================================
# CREATE DATE FEATURES
# ==========================================================

if "year" not in df.columns:
    df["year"] = df["date"].dt.year

if "month" not in df.columns:
    df["month"] = df["date"].dt.month

if "quarter" not in df.columns:
    df["quarter"] = df["date"].dt.quarter

if "day_name" not in df.columns:
    df["day_name"] = df["date"].dt.day_name()
    
# ==========================================================
# FILTERS
# ==========================================================

st.subheader("Filters")

c1, c2, c3, c4 = st.columns(4)

with c1:
    country = st.selectbox(
        "Country",
        ["All"] + sorted(df["country"].unique()),
        key="market_country"
    )

with c2:
    category = st.selectbox(
        "Category",
        ["All"] + sorted(df["category"].unique()),
        key="market_category"
    )

with c3:
    channel = st.selectbox(
        "Channel",
        ["All"] + sorted(df["channel"].unique()),
        key="market_channel"
    )

with c4:
    year = st.selectbox(
        "Year",
        ["All"] + sorted(df["year"].unique()),
        key="market_year"
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
    st.warning("No data available for the selected filters.")
    st.stop()
    
# ==========================================================
# SECTION 1 - EXECUTIVE MARKET KPIs
# ==========================================================

st.divider()

st.header("Executive Market KPIs")

# ----------------------------------------------------------
# KPI Calculations
# ----------------------------------------------------------

total_revenue = filtered["net_sales"].sum()

gross_sales = filtered["gross_sales"].sum()

total_units = filtered["units_sold"].sum()

average_selling_price = (
    total_revenue / total_units
    if total_units > 0 else 0
)

average_margin = filtered["margin_pct"].mean()

average_discount = filtered["discount_pct"].mean()

promotion_rate = (
    filtered["promo_flag"].mean() * 100
)

countries = filtered["country"].nunique()

cities = filtered["city"].nunique()

channels = filtered["channel"].nunique()

categories = filtered["category"].nunique()

brands = filtered["brand"].nunique()

products = filtered["sku_id"].nunique()

stores = filtered["store_id"].nunique()

# ----------------------------------------------------------
# Primary KPI Cards
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
    f"{total_units:,.0f}"
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
    "Promotion Rate",
    f"{promotion_rate:.1f}%"
)

# ----------------------------------------------------------
# Secondary KPI Cards
# ----------------------------------------------------------

k7, k8, k9, k10, k11, k12 = st.columns(6)

k7.metric(
    "Countries",
    f"{countries}"
)

k8.metric(
    "Cities",
    f"{cities}"
)

k9.metric(
    "Channels",
    f"{channels}"
)

k10.metric(
    "Categories",
    f"{categories}"
)

k11.metric(
    "Brands",
    f"{brands}"
)

k12.metric(
    "Products",
    f"{products}"
)

# ----------------------------------------------------------
# Market Coverage Summary
# ----------------------------------------------------------

st.subheader("Market Coverage Summary")

c1, c2, c3 = st.columns(3)

with c1:

    st.info(
        f"""
### Geographic Coverage

**Countries:** {countries}

**Cities:** {cities}

**Stores:** {stores}
"""
    )

with c2:

    st.info(
        f"""
### Product Portfolio

**Categories:** {categories}

**Brands:** {brands}

**Products:** {products}
"""
    )

with c3:

    st.info(
        f"""
### Sales Performance

**Channels:** {channels}

**Average Discount:** {average_discount:.1f}%

**Promotion Rate:** {promotion_rate:.1f}%
"""
    )

# ----------------------------------------------------------
# Executive Summary
# ----------------------------------------------------------

st.subheader("Executive Summary")

best_country = (
    filtered
    .groupby("country")["net_sales"]
    .sum()
    .idxmax()
)

best_category = (
    filtered
    .groupby("category")["net_sales"]
    .sum()
    .idxmax()
)

best_channel = (
    filtered
    .groupby("channel")["net_sales"]
    .sum()
    .idxmax()
)

best_brand = (
    filtered
    .groupby("brand")["net_sales"]
    .sum()
    .idxmax()
)

st.success(
    f"Total revenue across **{countries} countries** and **{cities} cities** is "
    f"**${total_revenue:,.0f}**."
)

st.info(
    f"The strongest market is **{best_country}**, while **{best_category}** is the highest revenue category."
)

st.info(
    f"The leading sales channel is **{best_channel}**, and the highest-performing brand is **{best_brand}**."
)

if average_margin >= 30:

    st.success(
        "Overall profitability is healthy with strong average margins."
    )

elif average_margin >= 20:

    st.info(
        "Profit margins are moderate and offer opportunities for optimization."
    )

else:

    st.warning(
        "Average profit margins are relatively low. Pricing and cost strategies should be reviewed."
    )

if promotion_rate >= 40:

    st.warning(
        "A significant proportion of sales occur under promotions. Consider evaluating long-term pricing sustainability."
    )

else:

    st.success(
        "Sales are not overly dependent on promotional campaigns."
    )
    
# ==========================================================
# SECTION 2 - MARKET PERFORMANCE
# ==========================================================

st.divider()

st.header("Market Performance")

# ----------------------------------------------------------
# Revenue by Country
# ----------------------------------------------------------

st.subheader("Revenue by Country")

country_sales = (
    filtered
    .groupby("country", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        Stores=("store_id", "nunique")
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
    color="Revenue",
    title="Revenue by Country"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=500,
    xaxis_title="Country",
    yaxis_title="Revenue ($)",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Top Performing Cities
# ----------------------------------------------------------

st.subheader("Top Performing Cities")

city_sales = (
    filtered
    .groupby(
        ["city", "country"],
        as_index=False
    )
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
    .head(15)
)

fig = px.bar(
    city_sales,
    x="Revenue",
    y="city",
    orientation="h",
    color="country",
    text="Revenue",
    title="Top 15 Revenue Generating Cities"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=600,
    xaxis_title="Revenue ($)",
    yaxis_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Global Market Distribution
# ----------------------------------------------------------

st.subheader("Global Market Distribution")

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
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum")
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
        "country": True,
        "Revenue": ":$,.0f",
        "Units": ":,.0f"
    },
    zoom=1,
    height=650
)

fig.update_layout(
    mapbox_style="open-street-map",
    template=THEME,
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Market Share by Country
# ----------------------------------------------------------

st.subheader("Market Share by Country")

country_share = country_sales.copy()

country_share["Market Share (%)"] = (
    country_share["Revenue"]
    /
    country_share["Revenue"].sum()
    * 100
)

fig = px.pie(
    country_share,
    names="country",
    values="Revenue",
    hole=0.55,
    title="Country Revenue Share"
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
# Country Performance Table
# ----------------------------------------------------------

st.subheader("Country Performance Summary")

country_table = country_share.copy()

country_table["Revenue"] = (
    country_table["Revenue"]
    .round(2)
)

country_table["Market Share (%)"] = (
    country_table["Market Share (%)"]
    .round(2)
)

st.dataframe(
    country_table,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Market Opportunity Matrix
# ----------------------------------------------------------

st.subheader("Market Opportunity Matrix")

market_matrix = (
    filtered
    .groupby("country", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Margin=("margin_pct", "mean"),
        Units=("units_sold", "sum")
    )
)

fig = px.scatter(
    market_matrix,
    x="Revenue",
    y="Margin",
    size="Units",
    color="Revenue",
    hover_name="country",
    title="Revenue vs Margin by Country"
)

fig.update_layout(
    template=THEME,
    height=600,
    xaxis_title="Revenue ($)",
    yaxis_title="Average Margin (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Market Insights
# ----------------------------------------------------------

st.subheader("Executive Market Insights")

best_country = country_sales.iloc[0]

best_city = city_sales.iloc[0]

largest_market_share = country_share.loc[
    country_share["Market Share (%)"].idxmax()
]

highest_margin_market = market_matrix.loc[
    market_matrix["Margin"].idxmax()
]

st.success(
    f"The highest revenue market is **{best_country['country']}** "
    f"with **${best_country['Revenue']:,.0f}** in sales."
)

st.info(
    f"The leading city is **{best_city['city']} ({best_city['country']})**, "
    f"generating **${best_city['Revenue']:,.0f}**."
)

st.info(
    f"**{largest_market_share['country']}** contributes "
    f"**{largest_market_share['Market Share (%)']:.1f}%** of total revenue."
)

st.info(
    f"The market with the highest average margin is "
    f"**{highest_margin_market['country']}** "
    f"({highest_margin_market['Margin']:.1f}% margin)."
)

if largest_market_share["Market Share (%)"] > 40:

    st.warning(
        "Revenue is highly concentrated in one market. Geographic diversification could reduce business risk."
    )

else:

    st.success(
        "Revenue is well distributed across multiple markets, reducing dependence on a single country."
    )
    
# ==========================================================
# SECTION 3 - SALES CHANNEL ANALYTICS
# ==========================================================

st.divider()

st.header("Sales Channel Analytics")

# ----------------------------------------------------------
# Channel Performance Summary
# ----------------------------------------------------------

channel_perf = (
    filtered
    .groupby("channel", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Gross_Sales=("gross_sales", "sum"),
        Units=("units_sold", "sum"),
        Avg_Margin=("margin_pct", "mean"),
        Avg_Discount=("discount_pct", "mean"),
        Promotion_Rate=("promo_flag", "mean")
    )
)

channel_perf["Promotion_Rate"] *= 100

# ----------------------------------------------------------
# Revenue by Channel
# ----------------------------------------------------------

left, right = st.columns(2)

fig = px.bar(
    channel_perf,
    x="channel",
    y="Revenue",
    color="Revenue",
    text="Revenue",
    title="Revenue by Sales Channel"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False,
    xaxis_title="Sales Channel",
    yaxis_title="Revenue ($)"
)

left.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Units Sold by Channel
# ----------------------------------------------------------

fig = px.bar(
    channel_perf,
    x="channel",
    y="Units",
    color="Units",
    text="Units",
    title="Units Sold by Channel"
)

fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False,
    xaxis_title="Sales Channel",
    yaxis_title="Units Sold"
)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Revenue Share by Channel
# ----------------------------------------------------------

st.subheader("Revenue Contribution by Channel")

fig = px.pie(
    channel_perf,
    names="channel",
    values="Revenue",
    hole=0.55,
    title="Channel Revenue Share"
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
# Margin vs Discount Analysis
# ----------------------------------------------------------

st.subheader("Margin vs Discount")

fig = px.scatter(
    channel_perf,
    x="Avg_Discount",
    y="Avg_Margin",
    size="Revenue",
    color="Revenue",
    hover_name="channel",
    text="channel",
    title="Average Margin vs Average Discount"
)

fig.update_traces(
    textposition="top center"
)

fig.update_layout(
    template=THEME,
    height=550,
    xaxis_title="Average Discount (%)",
    yaxis_title="Average Margin (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Promotion Rate by Channel
# ----------------------------------------------------------

st.subheader("Promotion Activity")

fig = px.bar(
    channel_perf,
    x="channel",
    y="Promotion_Rate",
    color="Promotion_Rate",
    text="Promotion_Rate",
    title="Promotion Rate by Channel"
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False,
    xaxis_title="Sales Channel",
    yaxis_title="Promotion Rate (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Channel Performance Table
# ----------------------------------------------------------

st.subheader("Channel Performance Summary")

channel_table = channel_perf.copy()

channel_table["Revenue"] = channel_table["Revenue"].round(2)
channel_table["Gross_Sales"] = channel_table["Gross_Sales"].round(2)
channel_table["Avg_Margin"] = channel_table["Avg_Margin"].round(2)
channel_table["Avg_Discount"] = channel_table["Avg_Discount"].round(2)
channel_table["Promotion_Rate"] = channel_table["Promotion_Rate"].round(2)

st.dataframe(
    channel_table,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Channel Insights
# ----------------------------------------------------------

st.subheader("Executive Channel Insights")

best_revenue = channel_perf.loc[
    channel_perf["Revenue"].idxmax()
]

best_margin = channel_perf.loc[
    channel_perf["Avg_Margin"].idxmax()
]

highest_discount = channel_perf.loc[
    channel_perf["Avg_Discount"].idxmax()
]

highest_promo = channel_perf.loc[
    channel_perf["Promotion_Rate"].idxmax()
]

st.success(
    f"The highest revenue channel is **{best_revenue['channel']}**, "
    f"generating **${best_revenue['Revenue']:,.0f}**."
)

st.info(
    f"The most profitable channel is **{best_margin['channel']}** "
    f"with an average margin of **{best_margin['Avg_Margin']:.1f}%**."
)

st.info(
    f"The highest average discount is offered through **{highest_discount['channel']}** "
    f"({highest_discount['Avg_Discount']:.1f}%)."
)

st.info(
    f"The most promotion-driven channel is **{highest_promo['channel']}** "
    f"with **{highest_promo['Promotion_Rate']:.1f}%** of transactions on promotion."
)

if best_margin["Avg_Margin"] > 30:

    st.success(
        "Current channel profitability is strong across the business."
    )

else:

    st.warning(
        "Profit margins across sales channels should be reviewed for optimization opportunities."
    )
    
# ==========================================================
# SECTION 4 - CATEGORY & BRAND MARKET SHARE
# ==========================================================

st.divider()

st.header("Category & Brand Market Share")

# ----------------------------------------------------------
# Category Performance
# ----------------------------------------------------------

category_perf = (
    filtered
    .groupby("category", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        Avg_Margin=("margin_pct", "mean")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

# ----------------------------------------------------------
# Brand Performance
# ----------------------------------------------------------

brand_perf = (
    filtered
    .groupby("brand", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        Avg_Margin=("margin_pct", "mean")
    )
    .sort_values(
        "Revenue",
        ascending=False
    )
)

# ----------------------------------------------------------
# Revenue by Category
# ----------------------------------------------------------

left, right = st.columns(2)

fig = px.bar(
    category_perf,
    x="category",
    y="Revenue",
    color="Revenue",
    text="Revenue",
    title="Revenue by Category"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False,
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

top_brands = brand_perf.head(15)

fig = px.bar(
    top_brands,
    x="Revenue",
    y="brand",
    orientation="h",
    color="Revenue",
    text="Revenue",
    title="Top 15 Brands by Revenue"
)

fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False,
    xaxis_title="Revenue ($)",
    yaxis_title=""
)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Category Market Share
# ----------------------------------------------------------

st.subheader("Category Revenue Share")

fig = px.pie(
    category_perf,
    names="category",
    values="Revenue",
    hole=0.55,
    title="Revenue Contribution by Category"
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
# Brand Market Share
# ----------------------------------------------------------

st.subheader("Brand Revenue Share")

brand_share = brand_perf.head(10)

fig = px.pie(
    brand_share,
    names="brand",
    values="Revenue",
    hole=0.55,
    title="Top 10 Brand Revenue Share"
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
# Category Profitability
# ----------------------------------------------------------

st.subheader("Category Profitability")

fig = px.scatter(
    category_perf,
    x="Revenue",
    y="Avg_Margin",
    size="Units",
    color="Revenue",
    text="category",
    title="Revenue vs Margin by Category"
)

fig.update_traces(
    textposition="top center"
)

fig.update_layout(
    template=THEME,
    height=600,
    xaxis_title="Revenue ($)",
    yaxis_title="Average Margin (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Category & Brand Summary Tables
# ----------------------------------------------------------

st.subheader("Portfolio Performance Summary")

left, right = st.columns(2)

left.dataframe(
    category_perf.round(2),
    hide_index=True,
    use_container_width=True
)

right.dataframe(
    brand_perf.head(15).round(2),
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Portfolio Insights
# ----------------------------------------------------------

st.subheader("Executive Portfolio Insights")

best_category = category_perf.iloc[0]

best_brand = brand_perf.iloc[0]

highest_margin_category = category_perf.loc[
    category_perf["Avg_Margin"].idxmax()
]

category_share = (
    best_category["Revenue"]
    /
    category_perf["Revenue"].sum()
    * 100
)

st.success(
    f"The highest revenue category is **{best_category['category']}**, generating **${best_category['Revenue']:,.0f}**."
)

st.info(
    f"The leading brand is **{best_brand['brand']}**, with revenue of **${best_brand['Revenue']:,.0f}**."
)

st.info(
    f"The most profitable category is **{highest_margin_category['category']}** "
    f"with an average margin of **{highest_margin_category['Avg_Margin']:.1f}%**."
)

st.info(
    f"The top category contributes **{category_share:.1f}%** of total revenue."
)

if category_share > 50:

    st.warning(
        "Revenue is highly concentrated in one category. Diversifying the product portfolio may reduce business risk."
    )

else:

    st.success(
        "Revenue is well distributed across multiple product categories."
    )
    
# ==========================================================
# SECTION 5 - CUSTOMER BUYING BEHAVIOUR & PROMOTION ANALYTICS
# ==========================================================

st.divider()

st.header("Customer Buying Behaviour & Promotion Analytics")

# ----------------------------------------------------------
# Promotion vs Non-Promotion Sales
# ----------------------------------------------------------

promotion_sales = (
    filtered
    .groupby("promo_flag", as_index=False)
    .agg(
        Revenue=("net_sales", "sum"),
        Units=("units_sold", "sum"),
        Avg_Discount=("discount_pct", "mean")
    )
)

promotion_sales["Promotion"] = promotion_sales["promo_flag"].map({
    0: "No Promotion",
    1: "Promotion"
})

left, right = st.columns(2)

fig = px.bar(
    promotion_sales,
    x="Promotion",
    y="Revenue",
    color="Promotion",
    text="Revenue",
    title="Revenue: Promotion vs Non-Promotion"
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

left.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Units Sold
# ----------------------------------------------------------

fig = px.bar(
    promotion_sales,
    x="Promotion",
    y="Units",
    color="Promotion",
    text="Units",
    title="Units Sold: Promotion vs Non-Promotion"
)

fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=450,
    showlegend=False
)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Discount Distribution
# ----------------------------------------------------------

st.subheader("Discount Distribution")

fig = px.histogram(
    filtered,
    x="discount_pct",
    nbins=25,
    color_discrete_sequence=["#1f77b4"],
    title="Distribution of Discounts"
)

fig.update_layout(
    template=THEME,
    height=450,
    xaxis_title="Discount (%)",
    yaxis_title="Transactions"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Discount vs Revenue
# ----------------------------------------------------------

st.subheader("Discount Impact on Revenue")

fig = px.scatter(
    filtered.sample(min(10000, len(filtered))),
    x="discount_pct",
    y="net_sales",
    color="promo_flag",
    trendline="ols",
    opacity=0.6,
    title="Discount Percentage vs Revenue"
)

fig.update_layout(
    template=THEME,
    height=550,
    xaxis_title="Discount (%)",
    yaxis_title="Revenue ($)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Promotion Rate by Category
# ----------------------------------------------------------

st.subheader("Promotion Activity by Category")

category_promo = (
    filtered
    .groupby("category", as_index=False)
    .agg(
        Promotion_Rate=("promo_flag", "mean"),
        Revenue=("net_sales", "sum")
    )
)

category_promo["Promotion_Rate"] *= 100

fig = px.bar(
    category_promo,
    x="category",
    y="Promotion_Rate",
    color="Revenue",
    text="Promotion_Rate",
    title="Promotion Rate by Category"
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template=THEME,
    height=500,
    yaxis_title="Promotion Rate (%)"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Promotion Rate by Sales Channel
# ----------------------------------------------------------

st.subheader("Promotion Activity by Channel")

channel_promo = (
    filtered
    .groupby("channel", as_index=False)
    .agg(
        Promotion_Rate=("promo_flag", "mean"),
        Revenue=("net_sales", "sum")
    )
)

channel_promo["Promotion_Rate"] *= 100

fig = px.bar(
    channel_promo,
    x="channel",
    y="Promotion_Rate",
    color="Promotion_Rate",
    text="Promotion_Rate",
    title="Promotion Rate by Sales Channel"
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
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

# ----------------------------------------------------------
# Executive Promotion Insights
# ----------------------------------------------------------

st.subheader("Executive Promotion Insights")

promo_revenue = promotion_sales.loc[
    promotion_sales["Promotion"] == "Promotion",
    "Revenue"
].sum()

promo_share = (
    promo_revenue /
    promotion_sales["Revenue"].sum()
    * 100
)

highest_category = category_promo.loc[
    category_promo["Promotion_Rate"].idxmax()
]

highest_channel = channel_promo.loc[
    channel_promo["Promotion_Rate"].idxmax()
]

avg_discount = filtered["discount_pct"].mean()

st.success(
    f"Promotional sales contribute **{promo_share:.1f}%** of total revenue."
)

st.info(
    f"Highest promotion activity occurs in **{highest_category['category']}** "
    f"({highest_category['Promotion_Rate']:.1f}% of transactions)."
)

st.info(
    f"The most promotion-driven sales channel is **{highest_channel['channel']}**."
)

st.info(
    f"The average customer discount across all transactions is **{avg_discount:.1f}%**."
)

if promo_share > 50:

    st.warning(
        "More than half of total revenue depends on promotions. Consider evaluating long-term pricing sustainability."
    )

else:

    st.success(
        "Revenue is not overly dependent on promotional campaigns."
    )
    
# ==========================================================
# SECTION 7 - EXECUTIVE MARKET DASHBOARD
# ==========================================================

st.divider()

st.header("Executive Market Dashboard")

# ----------------------------------------------------------
# Executive KPI Summary
# ----------------------------------------------------------

st.subheader("Market Performance Summary")

k1, k2, k3, k4 = st.columns(4)

market_revenue = filtered["net_sales"].sum()
market_units = filtered["units_sold"].sum()
market_margin = filtered["margin_pct"].mean()
promotion_rate = filtered["promo_flag"].mean() * 100

k1.metric(
    "Total Revenue",
    f"${market_revenue:,.0f}"
)

k2.metric(
    "Units Sold",
    f"{market_units:,.0f}"
)

k3.metric(
    "Average Margin",
    f"{market_margin:.1f}%"
)

k4.metric(
    "Promotion Rate",
    f"{promotion_rate:.1f}%"
)

# ----------------------------------------------------------
# Executive Scorecard
# ----------------------------------------------------------

st.subheader("Business Scorecard")

scorecard = pd.DataFrame({

    "Metric":[
        "Revenue",
        "Units Sold",
        "Average Margin (%)",
        "Promotion Rate (%)",
        "Categories",
        "Brands",
        "Countries",
        "Channels"
    ],

    "Value":[
        f"${market_revenue:,.0f}",
        f"{market_units:,.0f}",
        f"{market_margin:.1f}",
        f"{promotion_rate:.1f}",
        filtered["category"].nunique(),
        filtered["brand"].nunique(),
        filtered["country"].nunique(),
        filtered["channel"].nunique()
    ]

})

st.dataframe(
    scorecard,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Strategic Business Insights
# ----------------------------------------------------------

st.subheader("Strategic Business Insights")

top_country = (
    filtered.groupby("country")["net_sales"]
    .sum()
    .idxmax()
)

top_category = (
    filtered.groupby("category")["net_sales"]
    .sum()
    .idxmax()
)

top_brand = (
    filtered.groupby("brand")["net_sales"]
    .sum()
    .idxmax()
)

best_channel = (
    filtered.groupby("channel")["net_sales"]
    .sum()
    .idxmax()
)

highest_margin_category = (
    filtered.groupby("category")["margin_pct"]
    .mean()
    .idxmax()
)

st.success(
    f"Top revenue market: **{top_country}**."
)

st.success(
    f"Highest revenue category: **{top_category}**."
)

st.success(
    f"Leading brand: **{top_brand}**."
)

st.success(
    f"Best performing sales channel: **{best_channel}**."
)

st.info(
    f"Highest average margin is generated by **{highest_margin_category}**."
)

# ----------------------------------------------------------
# Executive Recommendations
# ----------------------------------------------------------

st.subheader("Strategic Recommendations")

recommendations = []

if promotion_rate > 50:
    recommendations.append(
        "Review pricing strategy because sales rely heavily on promotional activity."
    )

if market_margin < 25:
    recommendations.append(
        "Average product margin is relatively low. Consider improving pricing or supplier negotiations."
    )

if filtered["country"].nunique() < 3:
    recommendations.append(
        "Consider expanding into additional geographical markets."
    )

if filtered["channel"].nunique() == 1:
    recommendations.append(
        "Diversifying sales channels may improve resilience and revenue growth."
    )

if filtered["category"].nunique() < 5:
    recommendations.append(
        "Expanding the product portfolio may increase market reach."
    )

if len(recommendations) == 0:
    recommendations.append(
        "Current market performance appears balanced with no major strategic concerns."
    )

for rec in recommendations:
    st.info(rec)

# ----------------------------------------------------------
# Market Health Indicator
# ----------------------------------------------------------

st.subheader("Overall Market Health")

score = 100

if market_margin < 20:
    score -= 20

if promotion_rate > 60:
    score -= 15

if filtered["stock_out_flag"].mean() > 0.10:
    score -= 15

score = max(score, 0)

if score >= 85:

    st.success(
        f"Market Health Score: **{score}/100** — Excellent"
    )

elif score >= 70:

    st.info(
        f"Market Health Score: **{score}/100** — Good"
    )

elif score >= 50:

    st.warning(
        f"Market Health Score: **{score}/100** — Needs Improvement"
    )

else:

    st.error(
        f"Market Health Score: **{score}/100** — High Business Risk"
    )

# ----------------------------------------------------------
# Download Executive Report
# ----------------------------------------------------------

st.subheader("Download Executive Summary")

report = pd.DataFrame({

    "Metric":[
        "Revenue",
        "Units Sold",
        "Average Margin",
        "Promotion Rate",
        "Top Country",
        "Top Category",
        "Top Brand",
        "Top Channel",
        "Market Health Score"
    ],

    "Value":[
        market_revenue,
        market_units,
        round(market_margin,2),
        round(promotion_rate,2),
        top_country,
        top_category,
        top_brand,
        best_channel,
        score
    ]

})

csv = report.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Executive Market Report",
    data=csv,
    file_name="market_executive_summary.csv",
    mime="text/csv",
    use_container_width=True
)

# ----------------------------------------------------------
# Dashboard Footer
# ----------------------------------------------------------

st.caption(
    f"""
Customer & Market Analytics Dashboard

Records Analysed: {len(filtered):,}

Report Generated: {pd.Timestamp.now():%Y-%m-%d %H:%M}

Powered by Streamlit • Plotly • Pandas
"""
)