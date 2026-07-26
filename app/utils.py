import joblib
import pandas as pd
import streamlit as st

from config import DATA_FILE
from config import MODEL_FILE


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_FILE)

    df["date"] = pd.to_datetime(df["date"])

    return df


@st.cache_resource
def load_model():

    return joblib.load(MODEL_FILE)


@st.cache_data
def calculate_kpis(df):

    return {

        "Revenue": df["net_sales"].sum(),

        "Units": df["units_sold"].sum(),

        "Stores": df["store_id"].nunique(),

        "Countries": df["country"].nunique(),

        "Cities": df["city"].nunique(),

        "Products": df["sku_id"].nunique()

    }
    
def page_header(title, subtitle):

    st.title(title)

    st.caption(subtitle)

    st.divider()
    
def show_kpis(kpis):

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Revenue",
            f"${kpis['Revenue']:,.0f}"
        )

        st.metric(
            "Units Sold",
            f"{kpis['Units']:,.0f}"
        )

    with c2:

        st.metric(
            "Stores",
            kpis["Stores"]
        )

        st.metric(
            "Products",
            kpis["Products"]
        )

    with c3:

        st.metric(
            "Countries",
            kpis["Countries"]
        )

        st.metric(
            "Cities",
            kpis["Cities"]
        )
        
def apply_filters(df):

    country = st.selectbox(
        "Country",
        ["All"] + sorted(df["country"].unique().tolist())
    )

    if country != "All":
        df = df[df["country"] == country]

    category = st.selectbox(
        "Category",
        ["All"] + sorted(df["category"].unique().tolist())
    )

    if category != "All":
        df = df[df["category"] == category]

    channel = st.selectbox(
        "Channel",
        ["All"] + sorted(df["channel"].unique().tolist())
    )

    if channel != "All":
        df = df[df["channel"] == channel]

    return df

