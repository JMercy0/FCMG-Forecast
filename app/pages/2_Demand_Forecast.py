import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


from styles import load_css
from utils import load_data, page_header

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Demand Forecast",
    page_icon="🔮",
    layout="wide"
)

load_css()

page_header(
    "🔮 Demand Forecast",
    "Predict future product demand using the trained Random Forest model."
)

# ==========================================================
# LOAD DATA
# ==========================================================

df = load_data()


BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "models" / "fmcg_forecasting_model.pkl"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

st.divider()

st.subheader("Forecast Configuration")

c1, c2, c3 = st.columns(3)

with c1:
    country = st.selectbox(
        "Country",
        sorted(df["country"].unique()),
        key="forecast_country"
    )

with c2:
    city = st.selectbox(
        "City",
        sorted(
            df[df["country"] == country]["city"].unique()
        ),
        key="forecast_city"
    )

with c3:
    store = st.selectbox(
        "Store",
        sorted(
            df[
                (df["country"] == country) &
                (df["city"] == city)
            ]["store_id"].unique()
        ),
        key="forecast_store"
    )
    
c1, c2 = st.columns(2)

store_data = df[
    df["store_id"] == store
]

with c1:

    sku = st.selectbox(
        "Product (SKU)",
        sorted(store_data["sku_name"].unique()),
        key="forecast_sku"
    )

with c2:

    forecast_date = st.date_input(
        "Forecast Date"
    )
    
st.subheader("Business Inputs")

c1, c2, c3 = st.columns(3)

with c1:

    promotion = st.selectbox(
        "Promotion",
        ["No", "Yes"]
    )

with c2:

    discount = st.slider(
        "Discount %",
        0,
        100,
        10
    )

with c3:

    stock = st.number_input(
        "Current Stock",
        min_value=0,
        value=200
    )
    
c1, c2 = st.columns(2)

with c1:

    temperature = st.slider(
        "Temperature (°C)",
        -10.0,
        45.0,
        25.0
    )

with c2:

    rainfall = st.slider(
        "Rainfall (mm)",
        0.0,
        100.0,
        5.0
    )
    
st.divider()

predict = st.button(
    "🚀 Generate Forecast",
    use_container_width=True
)

# ==========================================================
# HISTORICAL SNAPSHOT
# ==========================================================

st.divider()
st.subheader("Historical Snapshot")

# ----------------------------------------------------------
# Retrieve Historical Data
# ----------------------------------------------------------

history = (
    df.loc[
        (df["store_id"] == store) &
        (df["sku_name"] == sku)
    ]
    .sort_values("date")
)

if history.empty:
    st.warning(
        "No historical records found for the selected Store and Product."
    )
    st.stop()

# ----------------------------------------------------------
# Latest Record
# ----------------------------------------------------------

latest = history.iloc[-1]

# ----------------------------------------------------------
# Historical Metrics
# ----------------------------------------------------------

avg_daily_demand = history["units_sold"].mean()

last_7_days_sales = history["units_sold"].tail(7).sum()

last_30_days_sales = history["units_sold"].tail(30).sum()

current_stock = latest["stock_on_hand"]

lead_time = latest["lead_time_days"]

promotion_status = "Yes" if latest["promo_flag"] == 1 else "No"

effective_price = (
    latest["list_price"] *
    (1 - latest["discount_pct"] / 100)
)

# ----------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------

row1 = st.columns(4)

row1[0].metric(
    "Average Daily Demand",
    f"{avg_daily_demand:.1f} Units"
)

row1[1].metric(
    "Last 7 Days Sales",
    f"{last_7_days_sales:.0f}"
)

row1[2].metric(
    "Last 30 Days Sales",
    f"{last_30_days_sales:.0f}"
)

row1[3].metric(
    "Current Stock",
    f"{current_stock:.0f}"
)

row2 = st.columns(3)

row2[0].metric(
    "Lead Time",
    f"{lead_time:.0f} Days"
)

row2[1].metric(
    "Promotion",
    promotion_status
)

row2[2].metric(
    "Effective Price",
    f"${effective_price:.2f}"
)

# ----------------------------------------------------------
# Product Information
# ----------------------------------------------------------

st.info(
    f"""
**Product Information**

- **SKU:** {latest["sku_name"]}
- **Brand:** {latest["brand"]}
- **Category:** {latest["category"]}
- **Store:** {store}
- **City:** {city}
- **Country:** {country}
"""
)

# ==========================================================
# STEP 3 - GENERATE DEMAND FORECAST
# ==========================================================

if predict:

    # ------------------------------------------------------
    # Historical Features
    # ------------------------------------------------------

    lag_1 = history["units_sold"].iloc[-1]

    lag_7 = history["units_sold"].tail(7).mean()

    lag_30 = history["units_sold"].tail(30).mean()

    lag_90 = history["units_sold"].tail(90).mean()

    rolling_mean_7 = history["units_sold"].tail(7).mean()

    rolling_mean_30 = history["units_sold"].tail(30).mean()

    rolling_std_7 = history["units_sold"].tail(7).std()

    if pd.isna(rolling_std_7):
        rolling_std_7 = 0

    # ------------------------------------------------------
    # Business Features
    # ------------------------------------------------------

    effective_price = (
        latest["list_price"] *
        (1 - discount / 100)
    )

    inventory_cover = stock / max(avg_daily_demand, 1)

    # ------------------------------------------------------
    # Calendar Features
    # ------------------------------------------------------

    month = forecast_date.month

    week = forecast_date.isocalendar().week

    quarter = ((month - 1) // 3) + 1

    # ------------------------------------------------------
    # Target Encoding
    # ------------------------------------------------------

    country_enc = (
        df.groupby("country")["units_sold"]
        .mean()
        .loc[country]
    )

    city_enc = (
        df.groupby("city")["units_sold"]
        .mean()
        .loc[city]
    )

    channel_enc = (
        df.groupby("channel")["units_sold"]
        .mean()
        .loc[latest["channel"]]
    )

    category_enc = (
        df.groupby("category")["units_sold"]
        .mean()
        .loc[latest["category"]]
    )

    brand_enc = (
        df.groupby("brand")["units_sold"]
        .mean()
        .loc[latest["brand"]]
    )

    sku_enc = (
        df.groupby("sku_id")["units_sold"]
        .mean()
        .loc[latest["sku_id"]]
    )

    # ------------------------------------------------------
    # Build Model Input
    # ------------------------------------------------------

    input_data = pd.DataFrame({

        "lag_1": [lag_1],
        "lag_7": [lag_7],
        "lag_30": [lag_30],
        "lag_90": [lag_90],

        "rolling_mean_7": [rolling_mean_7],
        "rolling_mean_30": [rolling_mean_30],
        "rolling_std_7": [rolling_std_7],

        "effective_price": [effective_price],

        "discount_pct": [discount],

        "promotion": [
            1 if promotion == "Yes" else 0
        ],

        "stock_on_hand": [stock],

        "inventory_cover": [inventory_cover],

        "lead_time_days": [lead_time],

        "temperature": [temperature],

        "rain_mm": [rainfall],

        "is_weekend": [latest["is_weekend"]],

        "is_holiday": [latest["is_holiday"]],

        "month": [month],

        "week": [week],

        "quarter": [quarter],

        "country_enc": [country_enc],

        "city_enc": [city_enc],

        "channel_enc": [channel_enc],

        "category_enc": [category_enc],

        "brand_enc": [brand_enc],

        "sku_enc": [sku_enc]

    })

    # ------------------------------------------------------
    # Align Feature Order With the Trained Model
    # ------------------------------------------------------
    # RandomForestRegressor (and most sklearn estimators) fitted on a
    # named DataFrame store the training column order in
    # `feature_names_in_`. Reindexing against that guarantees the
    # prediction input matches training order exactly, regardless of
    # how the dict above happens to be ordered.

    if hasattr(model, "feature_names_in_"):
        expected_features = list(model.feature_names_in_)

        missing = [f for f in expected_features if f not in input_data.columns]
        extra = [f for f in input_data.columns if f not in expected_features]

        if missing:
            st.error(
                f"Input is missing feature(s) the model was trained on: {missing}. "
                "Prediction cannot proceed until these are added."
            )
            st.stop()

        if extra:
            st.warning(
                f"Input contains feature(s) not seen during training (dropped): {extra}"
            )

        input_data = input_data[expected_features]
    else:
        st.warning(
            "Model has no recorded `feature_names_in_` (it may have been fit on a "
            "plain NumPy array). Falling back to the column order defined above — "
            "verify this matches Notebook 8's training order exactly."
        )

    # ------------------------------------------------------
    # Generate Prediction
    # ------------------------------------------------------

    prediction = model.predict(input_data)[0]

    # ------------------------------------------------------
    # Inventory Analysis
    # ------------------------------------------------------

    inventory_balance = stock - prediction

    inventory_coverage = stock / max(prediction, 1)

    # ------------------------------------------------------
    # Forecast Results
    # ------------------------------------------------------

    st.divider()

    st.subheader("Forecast Results")

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Forecast Demand",
        f"{prediction:.0f} Units"
    )

    m2.metric(
        "Inventory Balance",
        f"{inventory_balance:.0f} Units"
    )

    m3.metric(
        "Inventory Coverage",
        f"{inventory_coverage:.2f}x"
    )

    # ------------------------------------------------------
    # Recommendation Engine
    # ------------------------------------------------------

    st.subheader("Recommendation")

    if prediction > stock:

        reorder_qty = prediction - stock

        st.error(
            f"""
Current inventory is insufficient to satisfy the forecast demand.

Recommended reorder quantity:
**{reorder_qty:.0f} units**
"""
        )

    elif stock > prediction * 2:

        excess_stock = stock - prediction

        st.warning(
            f"""
Current inventory exceeds the forecast demand.

Estimated excess inventory:
**{excess_stock:.0f} units**
"""
        )

    else:

        st.success(
            """
Current inventory is appropriate for the expected demand.
"""
        )

    # ==========================================================
    # STEP 4 - FORECAST ANALYTICS
    # ==========================================================

    st.divider()
    st.header("Forecast Analytics")

    # ==========================================================
    # 4.1 HISTORICAL DEMAND TREND
    # ==========================================================

    st.subheader("Historical Demand Trend")

    history_chart = (
        history[["date", "units_sold"]]
        .tail(90)
        .copy()
    )

    history_chart["Type"] = "Historical"

    forecast_row = pd.DataFrame({

        "date": [forecast_date],

        "units_sold": [prediction],

        "Type": ["Forecast"]

    })

    trend = pd.concat(
        [history_chart, forecast_row],
        ignore_index=True
    )

    fig = px.line(

        trend,

        x="date",

        y="units_sold",

        color="Type",

        markers=True,

        title="Historical Demand and Forecast"

    )

    fig.update_layout(
        height=500,
        legend_title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ==========================================================
    # 4.2 FORECAST VS CURRENT STOCK
    # ==========================================================

    st.subheader("Demand vs Inventory")

    comparison = pd.DataFrame({

        "Metric": [

            "Forecast Demand",

            "Current Stock"

        ],

        "Units": [

            prediction,

            stock

        ]

    })

    fig = px.bar(

        comparison,

        x="Metric",

        y="Units",

        text="Units",

        color="Metric",

        title="Forecast Demand Compared with Available Inventory"

    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        height=450,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ==========================================================
    # 4.3 INVENTORY HEALTH
    # ==========================================================

    st.subheader("Inventory Health")

    coverage = stock / max(prediction, 1)

    if coverage < 1:

        st.error(
            "Inventory is below the forecast demand. Immediate replenishment is recommended."
        )

    elif coverage < 1.5:

        st.warning(
            "Inventory is sufficient but should be monitored closely."
        )

    elif coverage <= 3:

        st.success(
            "Inventory levels are healthy."
        )

    else:

        st.info(
            "Inventory is considerably higher than forecast demand."
        )

    # ==========================================================
    # 4.4 MODEL CONFIDENCE
    # ==========================================================

    st.subheader("Forecast Confidence")

    tree_predictions = np.array([
        tree.predict(input_data)[0]
        for tree in model.estimators_
    ])

    prediction_std = tree_predictions.std()

    confidence = max(
        0,
        min(100, 100 - prediction_std)
    )

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=confidence,

            number={"suffix": "%"},

            title={"text": "Model Confidence"},

            gauge={

                "axis": {"range": [0, 100]},

                "bar": {"color": "#1f77b4"},

                "steps": [

                    {
                        "range": [0, 50],
                        "color": "#ffcccc"
                    },

                    {
                        "range": [50, 80],
                        "color": "#fff2cc"
                    },

                    {
                        "range": [80, 100],
                        "color": "#d9ead3"
                    }

                ]

            }

        )

    )

    fig.update_layout(
        height=350
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        f"Prediction Standard Deviation: {prediction_std:.2f} Units"
    )

    # ==========================================================
    # 4.5 EXECUTIVE INSIGHTS
    # ==========================================================

    st.subheader("Executive Insights")

    insights = []

    if prediction > stock:

        insights.append(
            f"Forecast demand exceeds available inventory by **{prediction-stock:.0f} units**."
        )

    if stock > prediction * 2:

        insights.append(
            "Current inventory is substantially higher than the forecast demand."
        )

    if promotion == "Yes":

        insights.append(
            "The selected product is currently under promotion."
        )

    if discount > 20:

        insights.append(
            "A high discount level may significantly increase customer demand."
        )

    if rainfall > 30:

        insights.append(
            "Heavy rainfall may affect logistics and customer traffic."
        )

    if lead_time > 14:

        insights.append(
            "Supplier lead time is relatively long, increasing replenishment risk."
        )

    if confidence < 75:

        insights.append(
            "Model confidence is lower than expected. Interpret the forecast with caution."
        )

    if not insights:

        insights.append(
            "No significant operational risks detected for the selected forecast."
        )

    for insight in insights:

        st.info(insight)

    # ==========================================================
    # 4.6 DOWNLOAD FORECAST REPORT
    # ==========================================================

    st.subheader("Forecast Report")

    report = pd.DataFrame({

        "Forecast Date": [forecast_date],

        "Country": [country],

        "City": [city],

        "Store": [store],

        "SKU": [sku],

        "Forecast Demand": [round(prediction)],

        "Current Stock": [stock],

        "Inventory Balance": [round(inventory_balance)],

        "Inventory Coverage": [round(inventory_coverage, 2)],

        "Lead Time": [lead_time],

        "Promotion": [promotion],

        "Discount (%)": [discount]

    })

    st.dataframe(
        report,
        hide_index=True,
        use_container_width=True
    )

    csv = report.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="Download Forecast Report",

        data=csv,

        file_name="forecast_report.csv",

        mime="text/csv",

        use_container_width=True

    )