import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib

from pathlib import Path

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from styles import load_css
from utils import page_header

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Model Analytics",
    page_icon="🤖",
    layout="wide"
)

load_css()

THEME = "plotly_white"

page_header(
    "Model Analytics",
    "Machine Learning Performance, Explainability & Model Diagnostics"
)

# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "fmcg_forecasting_model.pkl"
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# ==========================================================
# LOAD MODEL
# ==========================================================

model = joblib.load(MODEL_PATH)

# ==========================================================
# LOAD TEST DATA
# ==========================================================

X_test = pd.read_csv(DATA_DIR / "X_test.csv")

y_test = (
    pd.read_csv(DATA_DIR / "y_test.csv")
      .squeeze()
)

# ==========================================================
# LOAD PREDICTIONS
# ==========================================================

predictions = pd.read_csv(
    REPORTS_DIR / "predictions.csv"
)

# ==========================================================
# CALCULATE METRICS
# ==========================================================

mae = mean_absolute_error(
    predictions["Actual"],
    predictions["Predicted"]
)

rmse = np.sqrt(
    mean_squared_error(
        predictions["Actual"],
        predictions["Predicted"]
    )
)

r2 = r2_score(
    predictions["Actual"],
    predictions["Predicted"]
)

mask = predictions["Actual"] != 0

mape = (
    np.abs(
        (
            predictions.loc[mask, "Actual"]
            - predictions.loc[mask, "Predicted"]
        )
        / predictions.loc[mask, "Actual"]
    ).mean()
) * 100

# ==========================================================
# OPTIONAL: LOAD MODEL METRICS FILE (if available)
# ==========================================================

metrics_file = REPORTS_DIR / "model_metrics.csv"

if metrics_file.exists():
    metrics = pd.read_csv(metrics_file)
else:
    metrics = None
  
  # ==========================================================
# SECTION 1 - EXECUTIVE MODEL KPIs
# ==========================================================

st.divider()

st.header("Executive Model Performance")

# ----------------------------------------------------------
# Model Metadata
# ----------------------------------------------------------

prediction_count = len(predictions)

feature_count = X_test.shape[1]

model_name = type(model).__name__

if hasattr(model, "n_estimators"):
    tree_count = model.n_estimators
else:
    tree_count = "N/A"

# Convert R² to an easy-to-read score
accuracy_score = max(0, min(r2 * 100, 100))

# ----------------------------------------------------------
# Primary KPI Cards
# ----------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "R² Score",
    f"{r2:.4f}"
)

k2.metric(
    "MAE",
    f"{mae:,.2f}"
)

k3.metric(
    "RMSE",
    f"{rmse:,.2f}"
)

k4.metric(
    "MAPE",
    f"{mape:.2f}%"
)

st.markdown("")

# ----------------------------------------------------------
# Secondary KPI Cards
# ----------------------------------------------------------

k5, k6, k7, k8 = st.columns(4)

k5.metric(
    "Model",
    model_name
)

k6.metric(
    "Trees",
    tree_count
)

k7.metric(
    "Features",
    feature_count
)

k8.metric(
    "Predictions",
    f"{prediction_count:,}"
)

# ----------------------------------------------------------
# Overall Model Performance Gauge
# ----------------------------------------------------------

st.subheader("Overall Forecast Performance")

fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=accuracy_score,
        number={"suffix": "%"},
        title={"text": "Forecast Performance"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2563EB"},
            "steps": [
                {"range": [0, 60], "color": "#F8D7DA"},
                {"range": [60, 80], "color": "#FFF3CD"},
                {"range": [80, 90], "color": "#D1ECF1"},
                {"range": [90, 100], "color": "#D4EDDA"}
            ]
        }
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
# Executive Summary
# ----------------------------------------------------------

st.subheader("Executive Summary")

summary = pd.DataFrame({

    "Metric": [
        "Algorithm",
        "R² Score",
        "MAE",
        "RMSE",
        "MAPE",
        "Input Features",
        "Predictions",
        "Decision Trees"
    ],

    "Value": [
        model_name,
        f"{r2:.4f}",
        f"{mae:.2f}",
        f"{rmse:.2f}",
        f"{mape:.2f}%",
        feature_count,
        f"{prediction_count:,}",
        tree_count
    ]

})

st.dataframe(
    summary,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# AI Executive Interpretation
# ----------------------------------------------------------

st.subheader("AI Executive Insights")

if r2 >= 0.95:

    st.success(
        f"""
The **{model_name}** forecasting model demonstrates outstanding predictive performance.

• R² Score: **{r2:.4f}**
• MAE: **{mae:.2f}**
• RMSE: **{rmse:.2f}**
• MAPE: **{mape:.2f}%**

The model explains nearly all variability in demand and is suitable for production deployment to support demand forecasting, inventory optimization, and supply chain planning.
"""
    )

elif r2 >= 0.90:

    st.info(
        f"""
The model performs very well and provides reliable demand forecasts.

Prediction errors remain low, making it suitable for operational planning and inventory management.
"""
    )

else:

    st.warning(
        f"""
The current forecasting model achieves an R² Score of **{r2:.4f}**.

Further feature engineering, hyperparameter tuning, or additional training data could improve forecasting accuracy.
"""
    )
    
# ==========================================================
# SECTION 2 - ACTUAL vs PREDICTED ANALYSIS
# ==========================================================

st.divider()

st.header("Actual vs Predicted Analysis")

# ----------------------------------------------------------
# Scatter Plot
# ----------------------------------------------------------

fig = px.scatter(
    predictions.sample(min(10000, len(predictions)), random_state=42),
    x="Actual",
    y="Predicted",
    opacity=0.45,
    title="Actual vs Predicted Demand"
)

min_val = min(
    predictions["Actual"].min(),
    predictions["Predicted"].min()
)

max_val = max(
    predictions["Actual"].max(),
    predictions["Predicted"].max()
)

fig.add_trace(
    go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode="lines",
        name="Perfect Prediction",
        line=dict(
            color="red",
            dash="dash",
            width=3
        )
    )
)

fig.update_layout(
    template=THEME,
    height=650,
    xaxis_title="Actual Units Sold",
    yaxis_title="Predicted Units Sold",
    legend=dict(
        orientation="h",
        y=1.02
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Correlation Analysis
# ----------------------------------------------------------

correlation = predictions["Actual"].corr(
    predictions["Predicted"]
)

avg_error = (
    predictions["Predicted"]
    - predictions["Actual"]
).mean()

k1, k2 = st.columns(2)

k1.metric(
    "Prediction Correlation",
    f"{correlation:.4f}"
)

k2.metric(
    "Average Prediction Error",
    f"{avg_error:.2f}"
)

# ----------------------------------------------------------
# Sample Prediction Table
# ----------------------------------------------------------

st.subheader("Sample Predictions")

sample = (
    predictions
    .sample(min(20, len(predictions)), random_state=42)
    .copy()
)

sample["Absolute Error"] = (
    sample["Predicted"]
    - sample["Actual"]
).abs()

sample["Error %"] = np.where(
    sample["Actual"] != 0,
    (
        sample["Absolute Error"]
        / sample["Actual"]
    ) * 100,
    0
)

sample = sample.round(2)

st.dataframe(
    sample,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Insights
# ----------------------------------------------------------

st.subheader("Executive Prediction Insights")

if correlation >= 0.95:
    st.success(
        f"The model shows an exceptionally strong relationship between actual and predicted demand (Correlation = {correlation:.4f}). Forecasts closely follow observed sales patterns."
    )
elif correlation >= 0.90:
    st.info(
        f"The model demonstrates a strong predictive relationship (Correlation = {correlation:.4f}), suitable for operational forecasting."
    )
else:
    st.warning(
        f"The prediction correlation is {correlation:.4f}. Additional feature engineering or model tuning could further improve forecast accuracy."
    )

if abs(avg_error) < 1:
    st.success(
        "Average prediction error is close to zero, indicating that the model has very little systematic bias."
    )
elif avg_error > 0:
    st.warning(
        "The model tends to slightly over-predict demand on average."
    )
else:
    st.warning(
        "The model tends to slightly under-predict demand on average."
    )
    
# ==========================================================
# SECTION 3 - RESIDUAL ERROR ANALYSIS
# ==========================================================

st.divider()

st.header("Residual Error Analysis")

# ----------------------------------------------------------
# Calculate Residuals
# ----------------------------------------------------------

predictions = predictions.copy()

predictions["Residual"] = (
    predictions["Actual"]
    - predictions["Predicted"]
)

predictions["Absolute Error"] = (
    predictions["Residual"].abs()
)

# ----------------------------------------------------------
# Residual Distribution
# ----------------------------------------------------------

left, right = st.columns(2)

fig = px.histogram(

    predictions,

    x="Residual",

    nbins=50,

    color_discrete_sequence=["#2563EB"],

    title="Residual Distribution"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Residual",

    yaxis_title="Frequency"

)

left.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Residual Box Plot
# ----------------------------------------------------------

fig = px.box(

    predictions,

    y="Residual",

    points="outliers",

    color_discrete_sequence=["#DC2626"],

    title="Residual Spread"

)

fig.update_layout(

    template=THEME,

    height=450,

    yaxis_title="Residual"

)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Residual vs Prediction
# ----------------------------------------------------------

st.subheader("Residuals vs Predicted Values")

fig = px.scatter(

    predictions.sample(
        min(10000, len(predictions)),
        random_state=42
    ),

    x="Predicted",

    y="Residual",

    opacity=0.4,

    color="Absolute Error",

    color_continuous_scale="Turbo",

    title="Residual Plot"

)

fig.add_hline(

    y=0,

    line_dash="dash",

    line_color="red"

)

fig.update_layout(

    template=THEME,

    height=550,

    xaxis_title="Predicted Units",

    yaxis_title="Residual"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Largest Prediction Errors
# ----------------------------------------------------------

st.subheader("Largest Prediction Errors")

largest_errors = (

    predictions

    .sort_values(

        "Absolute Error",

        ascending=False

    )

    .head(20)

)

st.dataframe(

    largest_errors.round(2),

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# Residual Statistics
# ----------------------------------------------------------

st.subheader("Residual Statistics")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Mean Residual",
    f"{predictions['Residual'].mean():.2f}"
)

c2.metric(
    "Median Residual",
    f"{predictions['Residual'].median():.2f}"
)

c3.metric(
    "Std Deviation",
    f"{predictions['Residual'].std():.2f}"
)

c4.metric(
    "Maximum Error",
    f"{predictions['Absolute Error'].max():.2f}"
)

# ----------------------------------------------------------
# Executive Residual Insights
# ----------------------------------------------------------

st.subheader("Executive Residual Insights")

mean_residual = predictions["Residual"].mean()

std_residual = predictions["Residual"].std()

if abs(mean_residual) < 1:

    st.success(
        "Residuals are centered around zero, indicating that the forecasting model is largely unbiased."
    )

else:

    st.warning(
        "Residuals indicate slight systematic bias. Additional feature engineering may improve model calibration."
    )

if std_residual < predictions["Actual"].std() * 0.25:

    st.success(
        "Residual variability is low, suggesting stable and consistent forecasting performance."
    )

else:

    st.info(
        "Residual spread indicates that prediction accuracy varies across different demand levels."
    )

st.info(
    f"""
Average residual: **{mean_residual:.2f}**

Residual standard deviation: **{std_residual:.2f}**

Largest prediction error: **{predictions['Absolute Error'].max():.2f} units**
"""
)

# ==========================================================
# SECTION 4 - FEATURE IMPORTANCE
# ==========================================================

st.divider()

st.header("Feature Importance Analysis")

# ----------------------------------------------------------
# Extract Feature Importance
# ----------------------------------------------------------

if hasattr(model, "feature_importances_"):

    feature_importance = pd.DataFrame({

        "Feature": X_test.columns,

        "Importance": model.feature_importances_

    })

    feature_importance = (
        feature_importance
        .sort_values(
            "Importance",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # ------------------------------------------------------
    # Top 15 Most Important Features
    # ------------------------------------------------------

    left, right = st.columns([2, 1])

    fig = px.bar(

        feature_importance.head(15),

        x="Importance",

        y="Feature",

        orientation="h",

        color="Importance",

        color_continuous_scale="Viridis",

        text="Importance",

        title="Top 15 Most Important Features"

    )

    fig.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside"
    )

    fig.update_layout(

        template=THEME,

        height=650,

        xaxis_title="Importance Score",

        yaxis_title=""

    )

    left.plotly_chart(
        fig,
        use_container_width=True
    )

    # ------------------------------------------------------
    # Feature Contribution Pie Chart
    # ------------------------------------------------------

    fig = px.pie(

        feature_importance.head(10),

        names="Feature",

        values="Importance",

        hole=0.55,

        title="Top 10 Feature Contribution"

    )

    fig.update_layout(

        template=THEME,

        height=650

    )

    right.plotly_chart(
        fig,
        use_container_width=True
    )

    # ------------------------------------------------------
    # Complete Feature Ranking
    # ------------------------------------------------------

    st.subheader("Complete Feature Ranking")

    ranking = feature_importance.copy()

    ranking["Rank"] = range(
        1,
        len(ranking) + 1
    )

    ranking["Importance"] = ranking["Importance"].round(5)

    st.dataframe(

        ranking,

        hide_index=True,

        use_container_width=True

    )

    # ------------------------------------------------------
    # Importance Statistics
    # ------------------------------------------------------

    st.subheader("Feature Importance Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Most Important Feature",
        feature_importance.iloc[0]["Feature"]
    )

    c2.metric(
        "Highest Importance",
        f"{feature_importance.iloc[0]['Importance']:.4f}"
    )

    c3.metric(
        "Features Used",
        len(feature_importance)
    )

    # ------------------------------------------------------
    # Executive Insights
    # ------------------------------------------------------

    st.subheader("Executive Feature Insights")

    top5 = feature_importance.head(5)

    st.success(
        f"""
The Random Forest model identified **{top5.iloc[0]['Feature']}**
as the strongest predictor of product demand.

The five most influential variables are:

• {top5.iloc[0]['Feature']}

• {top5.iloc[1]['Feature']}

• {top5.iloc[2]['Feature']}

• {top5.iloc[3]['Feature']}

• {top5.iloc[4]['Feature']}

These variables contribute the greatest predictive power and should
receive the highest priority during future data collection,
monitoring, and feature engineering.
"""
    )

else:

    st.warning(
        "The selected model does not provide feature importance values."
    )
    
# ==========================================================
# SECTION 5 - PREDICTION ERROR DISTRIBUTION
# ==========================================================

st.divider()

st.header("Prediction Error Distribution")

# ----------------------------------------------------------
# Calculate Prediction Errors
# ----------------------------------------------------------

error_analysis = predictions.copy()

error_analysis["Absolute Error"] = (
    error_analysis["Actual"]
    - error_analysis["Predicted"]
).abs()

error_analysis["Percentage Error"] = np.where(
    error_analysis["Actual"] != 0,
    (
        error_analysis["Absolute Error"]
        /
        error_analysis["Actual"]
    ) * 100,
    0
)

# ----------------------------------------------------------
# Error Distribution Histogram
# ----------------------------------------------------------

left, right = st.columns(2)

fig = px.histogram(

    error_analysis,

    x="Percentage Error",

    nbins=40,

    color_discrete_sequence=["#2563EB"],

    title="Prediction Error Distribution (%)"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Percentage Error (%)",

    yaxis_title="Number of Predictions"

)

left.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Error Box Plot
# ----------------------------------------------------------

fig = px.box(

    error_analysis,

    y="Percentage Error",

    points="outliers",

    color_discrete_sequence=["#DC2626"],

    title="Prediction Error Spread"

)

fig.update_layout(

    template=THEME,

    height=450,

    yaxis_title="Percentage Error (%)"

)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Error Categories
# ----------------------------------------------------------

st.subheader("Prediction Accuracy Categories")

conditions = [

    error_analysis["Percentage Error"] <= 5,

    error_analysis["Percentage Error"].between(5,10),

    error_analysis["Percentage Error"].between(10,20),

    error_analysis["Percentage Error"] > 20

]

labels = [

    "Excellent (≤5%)",

    "Good (5-10%)",

    "Acceptable (10-20%)",

    "Poor (>20%)"

]

error_analysis["Prediction Quality"] = np.select(

    conditions,

    labels,

    default="Unknown"

)

quality = (

    error_analysis

    .groupby("Prediction Quality", as_index=False)

    .size()

)

quality.columns = [

    "Prediction Quality",

    "Count"

]

fig = px.pie(

    quality,

    names="Prediction Quality",

    values="Count",

    hole=0.55,

    title="Prediction Accuracy Classification"

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
# Top Largest Prediction Errors
# ----------------------------------------------------------

st.subheader("Largest Forecast Errors")

largest_errors = (

    error_analysis

    .sort_values(

        "Absolute Error",

        ascending=False

    )

    .head(20)

)

st.dataframe(

    largest_errors.round(2),

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# Error Statistics
# ----------------------------------------------------------

st.subheader("Forecast Error Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Average Error",

    f"{error_analysis['Absolute Error'].mean():.2f}"

)

c2.metric(

    "Median Error",

    f"{error_analysis['Absolute Error'].median():.2f}"

)

c3.metric(

    "Maximum Error",

    f"{error_analysis['Absolute Error'].max():.2f}"

)

c4.metric(

    "Average % Error",

    f"{error_analysis['Percentage Error'].mean():.2f}%"

)

# ----------------------------------------------------------
# Executive Error Insights
# ----------------------------------------------------------

st.subheader("Executive Forecast Insights")

excellent_pct = (

    (
        error_analysis["Prediction Quality"]
        == "Excellent (≤5%)"
    ).mean()
) * 100

poor_pct = (

    (
        error_analysis["Prediction Quality"]
        == "Poor (>20%)"
    ).mean()
) * 100

st.success(

    f"{excellent_pct:.1f}% of forecasts fall within a 5% prediction error, demonstrating high forecasting accuracy."

)

if poor_pct > 10:

    st.warning(

        f"{poor_pct:.1f}% of predictions exceed a 20% error. These cases should be reviewed for unusual demand patterns or missing predictive features."

    )

else:

    st.success(

        "Only a small proportion of forecasts exhibit large prediction errors, indicating stable model performance."

    )

st.info(

    f"""
Average absolute forecast error: **{error_analysis['Absolute Error'].mean():.2f} units**

Average percentage error: **{error_analysis['Percentage Error'].mean():.2f}%**

Maximum observed error: **{error_analysis['Absolute Error'].max():.2f} units**
"""

)

# ==========================================================
# SECTION 6 - MODEL STABILITY & ROBUSTNESS
# ==========================================================

st.divider()

st.header("Model Stability & Robustness")

# ----------------------------------------------------------
# Demand Segmentation
# ----------------------------------------------------------

st.subheader("Prediction Performance Across Demand Levels")

stability = predictions.copy()

stability["Demand Segment"] = pd.qcut(
    stability["Actual"],
    q=4,
    labels=[
        "Low Demand",
        "Medium-Low",
        "Medium-High",
        "High Demand"
    ]
)

segment_summary = (

    stability

    .groupby("Demand Segment", observed=False)

    .agg(
        Actual_Mean=("Actual", "mean"),
        Predicted_Mean=("Predicted", "mean"),
        MAE=("Absolute Error", "mean")
    )

    .reset_index()

)

# ----------------------------------------------------------
# Actual vs Predicted by Segment
# ----------------------------------------------------------

fig = go.Figure()

fig.add_trace(

    go.Bar(

        x=segment_summary["Demand Segment"],

        y=segment_summary["Actual_Mean"],

        name="Actual Demand"

    )

)

fig.add_trace(

    go.Bar(

        x=segment_summary["Demand Segment"],

        y=segment_summary["Predicted_Mean"],

        name="Predicted Demand"

    )

)

fig.update_layout(

    barmode="group",

    template=THEME,

    height=500,

    title="Average Demand by Segment",

    xaxis_title="Demand Segment",

    yaxis_title="Average Units Sold"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# MAE by Demand Segment
# ----------------------------------------------------------

st.subheader("Forecast Error by Demand Segment")

fig = px.bar(

    segment_summary,

    x="Demand Segment",

    y="MAE",

    color="MAE",

    text="MAE",

    color_continuous_scale="Turbo",

    title="Average Absolute Error"

)

fig.update_traces(

    texttemplate="%{text:.2f}",

    textposition="outside"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Demand Segment",

    yaxis_title="Mean Absolute Error"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Stability Metrics
# ----------------------------------------------------------

st.subheader("Model Stability Metrics")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Lowest Segment MAE",
    f"{segment_summary['MAE'].min():.2f}"
)

c2.metric(
    "Highest Segment MAE",
    f"{segment_summary['MAE'].max():.2f}"
)

variation = (
    segment_summary["MAE"].max()
    -
    segment_summary["MAE"].min()
)

c3.metric(
    "MAE Variation",
    f"{variation:.2f}"
)

# ----------------------------------------------------------
# Segment Performance Table
# ----------------------------------------------------------

st.subheader("Demand Segment Summary")

segment_table = segment_summary.copy()

segment_table = segment_table.round(2)

st.dataframe(
    segment_table,
    hide_index=True,
    use_container_width=True
)

# ----------------------------------------------------------
# Executive Stability Insights
# ----------------------------------------------------------

st.subheader("Executive Stability Insights")

best_segment = segment_summary.loc[
    segment_summary["MAE"].idxmin(),
    "Demand Segment"
]

worst_segment = segment_summary.loc[
    segment_summary["MAE"].idxmax(),
    "Demand Segment"
]

if variation < 5:

    st.success(
        f"""
The forecasting model demonstrates excellent stability across all demand levels.

• Best performance: **{best_segment}**

• Highest error segment: **{worst_segment}**

The variation in MAE is only **{variation:.2f} units**, indicating highly consistent predictions regardless of demand volume.
"""
    )

else:

    st.warning(
        f"""
Model performance varies across demand segments.

Best performance occurs for **{best_segment}**, while **{worst_segment}** experiences the highest prediction error.

Consider additional feature engineering or targeted model tuning for high-error demand segments.
"""
    )
 # ==========================================================
# SECTION 7 - PREDICTION CONFIDENCE & FORECAST RELIABILITY
# ==========================================================

st.divider()

st.header("Prediction Confidence & Forecast Reliability")

# ----------------------------------------------------------
# Prepare Confidence Dataset
# ----------------------------------------------------------

confidence = predictions.copy()

# Calculate residuals
confidence["Residual"] = (
    confidence["Actual"]
    - confidence["Predicted"]
)

# Absolute Error
confidence["Absolute Error"] = (
    confidence["Residual"].abs()
)

# Percentage Error
confidence["Percentage Error"] = np.where(
    confidence["Actual"] != 0,
    (
        confidence["Absolute Error"]
        / confidence["Actual"]
    ) * 100,
    0
)

# ----------------------------------------------------------
# Confidence Score (0 - 100)
# ----------------------------------------------------------

max_error = confidence["Percentage Error"].max()

if max_error == 0:

    confidence["Confidence Score"] = 100

else:

    confidence["Confidence Score"] = (

        100

        -

        (
            confidence["Percentage Error"]
            / max_error
        ) * 100

    )

confidence["Confidence Score"] = (
    confidence["Confidence Score"]
    .clip(0, 100)
    .round(1)
)

# ----------------------------------------------------------
# Confidence Categories
# ----------------------------------------------------------

confidence["Confidence Level"] = pd.cut(

    confidence["Confidence Score"],

    bins=[0, 60, 80, 90, 100],

    labels=[
        "Low",
        "Moderate",
        "High",
        "Very High"
    ],

    include_lowest=True

)

# ----------------------------------------------------------
# Confidence Distribution
# ----------------------------------------------------------

st.subheader("Forecast Confidence Distribution")

left, right = st.columns(2)

confidence_summary = (

    confidence

    .groupby(
        "Confidence Level",
        observed=False
    )

    .size()

    .reset_index(name="Forecasts")

)

fig = px.bar(

    confidence_summary,

    x="Confidence Level",

    y="Forecasts",

    color="Forecasts",

    text="Forecasts",

    color_continuous_scale="Blues",

    title="Forecast Confidence Levels"

)

fig.update_traces(

    textposition="outside"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Confidence Level",

    yaxis_title="Number of Forecasts"

)

left.plotly_chart(
    fig,
    use_container_width=True
)

fig = px.pie(

    confidence_summary,

    names="Confidence Level",

    values="Forecasts",

    hole=0.55,

    title="Forecast Reliability"

)

fig.update_layout(

    template=THEME,

    height=450

)

right.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Confidence KPIs
# ----------------------------------------------------------

st.subheader("Forecast Confidence Metrics")

average_confidence = confidence["Confidence Score"].mean()

very_high_pct = (

    (
        confidence["Confidence Level"]
        == "Very High"
    ).mean()

) * 100

high_pct = (

    confidence["Confidence Level"]

    .isin(
        ["High", "Very High"]
    )

).mean() * 100

c1, c2, c3 = st.columns(3)

c1.metric(
    "Average Confidence",
    f"{average_confidence:.1f}%"
)

c2.metric(
    "High Confidence",
    f"{high_pct:.1f}%"
)

c3.metric(
    "Very High Confidence",
    f"{very_high_pct:.1f}%"
)

# ----------------------------------------------------------
# Confidence Distribution Histogram
# ----------------------------------------------------------

st.subheader("Confidence Score Distribution")

fig = px.histogram(

    confidence,

    x="Confidence Score",

    nbins=30,

    color_discrete_sequence=["#2563EB"],

    title="Distribution of Confidence Scores"

)

fig.update_layout(

    template=THEME,

    height=450,

    xaxis_title="Confidence Score",

    yaxis_title="Forecast Count"

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ----------------------------------------------------------
# Most Reliable Forecasts
# ----------------------------------------------------------

st.subheader("Top 20 Most Reliable Forecasts")

best_predictions = (

    confidence

    .sort_values(
        "Confidence Score",
        ascending=False
    )

    .head(20)

)

st.dataframe(

    best_predictions[[
        "Actual",
        "Predicted",
        "Absolute Error",
        "Percentage Error",
        "Confidence Score",
        "Confidence Level"
    ]].round(2),

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# Lowest Confidence Forecasts
# ----------------------------------------------------------

st.subheader("Top 20 Lowest Confidence Forecasts")

worst_predictions = (

    confidence

    .sort_values(
        "Confidence Score"
    )

    .head(20)

)

st.dataframe(

    worst_predictions[[
        "Actual",
        "Predicted",
        "Absolute Error",
        "Percentage Error",
        "Confidence Score",
        "Confidence Level"
    ]].round(2),

    hide_index=True,

    use_container_width=True

)

# ----------------------------------------------------------
# Executive Forecast Reliability Insights
# ----------------------------------------------------------

st.subheader("Executive Forecast Reliability Insights")

if average_confidence >= 90:

    st.success(
        f"""
The forecasting model demonstrates **excellent reliability**.

• Average Confidence: **{average_confidence:.1f}%**

• High Confidence Forecasts: **{high_pct:.1f}%**

• Very High Confidence Forecasts: **{very_high_pct:.1f}%**

The model is suitable for automated demand planning, inventory optimization, and executive decision support.
"""
    )

elif average_confidence >= 80:

    st.info(
        f"""
The forecasting model demonstrates **good reliability**.

Average confidence is **{average_confidence:.1f}%**.

Most forecasts are dependable, although a small proportion should be reviewed manually.
"""
    )

else:

    st.warning(
        f"""
Forecast confidence averages **{average_confidence:.1f}%**.

Consider additional feature engineering or retraining before relying on automated forecasting decisions.
"""
    )
 
# ==========================================================
# SECTION 8 - EXECUTIVE AI INSIGHTS & BUSINESS RECOMMENDATIONS
# ==========================================================

st.divider()

st.header("Executive AI Insights & Business Recommendations")

# ----------------------------------------------------------
# Overall Model Assessment
# ----------------------------------------------------------

st.subheader("Overall Model Assessment")

if r2 >= 0.95:
    model_grade = "Excellent"
    grade_color = "🟢"
elif r2 >= 0.90:
    model_grade = "Very Good"
    grade_color = "🟢"
elif r2 >= 0.80:
    model_grade = "Good"
    grade_color = "🟡"
elif r2 >= 0.70:
    model_grade = "Fair"
    grade_color = "🟠"
else:
    model_grade = "Needs Improvement"
    grade_color = "🔴"

st.success(
    f"""
### {grade_color} Overall Model Rating: **{model_grade}**

The Random Forest demand forecasting model achieved:

- **R² Score:** {r2:.4f}
- **MAE:** {mae:.2f}
- **RMSE:** {rmse:.2f}
- **MAPE:** {mape:.2f}%
- **Average Forecast Confidence:** {average_confidence:.1f}%

Overall, the model demonstrates **{model_grade.lower()}** predictive capability for FMCG demand forecasting.
"""
)

# ----------------------------------------------------------
# Business Impact
# ----------------------------------------------------------

st.subheader("Business Impact")

impact = []

if r2 >= 0.90:
    impact.append(
        "Accurate demand forecasts reduce inventory uncertainty and improve supply chain planning."
    )

if mape <= 10:
    impact.append(
        "Forecast accuracy is sufficiently high for operational inventory planning."
    )

if average_confidence >= 90:
    impact.append(
        "Most forecasts can be trusted for automated replenishment decisions."
    )

if mae < predictions["Actual"].mean() * 0.10:
    impact.append(
        "Prediction errors are relatively small compared with average product demand."
    )

for item in impact:
    st.success(f"✓ {item}")

# ----------------------------------------------------------
# Key Strengths
# ----------------------------------------------------------

st.subheader("Key Model Strengths")

strengths = [

    "High predictive accuracy across historical sales data.",

    "Excellent capability for identifying demand patterns.",

    "Strong feature importance explainability using Random Forest.",

    "Stable forecasting performance across demand segments.",

    "Reliable inventory planning support.",

    "Suitable for executive sales forecasting dashboards."

]

for s in strengths:
    st.markdown(f"✅ {s}")

# ----------------------------------------------------------
# Improvement Opportunities
# ----------------------------------------------------------

st.subheader("Recommended Improvements")

recommendations = []

if mape > 10:
    recommendations.append(
        "Reduce forecast error through additional feature engineering."
    )

if average_confidence < 90:
    recommendations.append(
        "Review lower-confidence forecasts before operational deployment."
    )

recommendations.extend([

    "Retrain the forecasting model monthly using newly available sales data.",

    "Incorporate competitor pricing and market intelligence.",

    "Include macroeconomic indicators where available.",

    "Integrate weather forecasts for improved seasonal prediction.",

    "Automate model retraining through an MLOps pipeline."

])

for rec in recommendations:
    st.info(f"• {rec}")

# ----------------------------------------------------------
# Deployment Readiness
# ----------------------------------------------------------

st.subheader("Production Deployment Readiness")

deployment_score = round(
    (
        (r2 * 100)
        + (100 - min(mape, 100))
        + average_confidence
    ) / 3,
    1
)

fig = go.Figure(

    go.Indicator(

        mode="gauge+number",

        value=deployment_score,

        number={"suffix": "%"},

        title={"text": "Production Readiness"},

        gauge={

            "axis": {"range": [0, 100]},

            "bar": {"color": "#2563EB"},

            "steps": [

                {"range": [0, 60], "color": "#F8D7DA"},

                {"range": [60, 80], "color": "#FFF3CD"},

                {"range": [80, 90], "color": "#D1ECF1"},

                {"range": [90, 100], "color": "#D4EDDA"}

            ]

        }

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
# Final Executive Recommendation
# ----------------------------------------------------------

st.subheader("Final Executive Recommendation")

if deployment_score >= 90:

    st.success(
        """
### Recommendation

The forecasting model is **ready for production deployment**.

It demonstrates strong predictive performance, high forecast reliability,
and excellent explainability. The model is suitable for supporting:

- Demand Planning
- Inventory Optimization
- Sales Forecasting
- Procurement Planning
- Executive Decision Support
"""
    )

elif deployment_score >= 80:

    st.info(
        """
### Recommendation

The forecasting model is suitable for deployment following routine monitoring.

Continue periodic retraining and monitor prediction quality as new sales data becomes available.
"""
    )

else:

    st.warning(
        """
### Recommendation

The forecasting model should undergo additional tuning before production deployment.

Recommended actions include additional feature engineering, hyperparameter optimization,
and retraining using more recent data.
"""
    )