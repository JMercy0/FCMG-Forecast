import streamlit as st

from styles import load_css
from utils import load_data
from utils import calculate_kpis

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="FMCG Demand Forecasting",
    layout="wide"
)

load_css()

df = load_data()
kpis = calculate_kpis(df)

# ---------------------------------------------------
# Theme: deep-purple glow (scoped to this page)
# ---------------------------------------------------

st.markdown("""
<style>

@keyframes bgPulse {
    0%   { background-position: 50% 50%; }
    50%  { background-position: 50% 60%; }
    100% { background-position: 50% 50%; }
}

@keyframes orbGlow {
    0%   { box-shadow: 0 0 25px 8px rgba(139,92,246,0.45), 0 0 60px 20px rgba(76,29,149,0.35); }
    50%  { box-shadow: 0 0 40px 14px rgba(139,92,246,0.7), 0 0 90px 30px rgba(76,29,149,0.5); }
    100% { box-shadow: 0 0 25px 8px rgba(139,92,246,0.45), 0 0 60px 20px rgba(76,29,149,0.35); }
}

@keyframes ringExpand {
    0%   { transform: scale(0.9); opacity: 0.6; }
    70%  { transform: scale(1.35); opacity: 0; }
    100% { transform: scale(1.35); opacity: 0; }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}

.stApp {
    background: radial-gradient(circle at 50% 35%, #3b2478 0%, #241457 35%, #140b33 70%, #0a0620 100%);
    background-size: 140% 140%;
    animation: bgPulse 14s ease-in-out infinite;
}

.hero-wrap {
    position: relative;
    text-align: center;
    padding: 3.5rem 1rem 2.5rem 1rem;
    margin-bottom: 1.5rem;
    overflow: hidden;
}

.orb-stage {
    position: relative;
    width: 110px;
    height: 110px;
    margin: 0 auto 1.5rem auto;
}
.orb-ring {
    position: absolute;
    top: 50%; left: 50%;
    width: 110px; height: 110px;
    margin-top: -55px; margin-left: -55px;
    border: 1.5px solid rgba(167,139,250,0.5);
    border-radius: 50%;
    animation: ringExpand 3s ease-out infinite;
}
.orb-ring.delay1 { animation-delay: 1s; }
.orb-ring.delay2 { animation-delay: 2s; }
.orb-core {
    position: absolute;
    top: 50%; left: 50%;
    width: 62px; height: 62px;
    margin-top: -31px; margin-left: -31px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 30%, #1a0f38, #0a0620 70%);
    background: linear-gradient(135deg, #a78bfa, #6d28d9 45%, #0a0620 70%);
    animation: orbGlow 3s ease-in-out infinite;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 600;
    letter-spacing: 1px;
    color: #ffffff !important;
    text-shadow: 0 0 20px rgba(255,255,255,0.35), 0 0 45px rgba(167,139,250,0.5);
    margin: 0;
    animation: fadeUp 0.8s ease-out;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #b8a9e0;
    margin-top: 0.6rem;
    animation: fadeUp 0.8s ease-out 0.15s backwards;
}
.hero-meta {
    font-size: 0.75rem;
    letter-spacing: 2px;
    color: #8875b8;
    text-transform: uppercase;
    margin-top: 0.4rem;
    animation: fadeUp 0.8s ease-out 0.3s backwards;
}

.kpi-row {
    display: flex;
    gap: 0.9rem;
    flex-wrap: wrap;
    margin-bottom: 1.8rem;
}
.kpi-card {
    flex: 1;
    min-width: 140px;
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 14px;
    padding: 1.1rem 0.6rem;
    text-align: center;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(6px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.kpi-card:hover {
    transform: translateY(-4px);
    border-color: rgba(167,139,250,0.7);
    box-shadow: 0 8px 24px rgba(109,40,217,0.35);
}
.kpi-card .kpi-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #a99bd4;
    margin-bottom: 0.35rem;
}
.kpi-card .kpi-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f5f3ff;
}

.section-title {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #c4b5fd;
    padding-bottom: 0.5rem;
    margin: 1.8rem 0 1.1rem 0;
    font-weight: 600;
    border-bottom: 1px solid rgba(167,139,250,0.25);
}

.tag {
    display: inline-block;
    border: 1px solid rgba(167,139,250,0.4);
    border-radius: 20px;
    padding: 0.25rem 0.9rem;
    margin: 0.2rem 0.35rem 0.2rem 0;
    font-size: 0.8rem;
    color: #e4d9ff;
    background: rgba(139,92,246,0.12);
    transition: all 0.25s ease;
}
.tag:hover {
    background: rgba(139,92,246,0.3);
    border-color: rgba(167,139,250,0.9);
}

.module-card {
    position: relative;
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 14px;
    padding: 1.5rem 1rem;
    text-align: center;
    height: 100%;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(6px);
    margin-bottom: 0.9rem;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.module-card:hover {
    transform: translateY(-5px);
    border-color: rgba(167,139,250,0.85);
    box-shadow: 0 10px 30px rgba(109,40,217,0.45);
}
.module-card .module-title {
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f5f3ff;
    margin-bottom: 0.4rem;
}
.module-card .module-caption {
    font-size: 0.82rem;
    color: #a99bd4;
}

/* Clickable module cards (st.container(border=True) + st.page_link) */
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stPageLink"]) {
    border: 1px solid rgba(167,139,250,0.25) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(6px);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    text-align: center;
    padding: 0.4rem 0.2rem 0.8rem 0.2rem;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stPageLink"]):hover {
    transform: translateY(-5px);
    border-color: rgba(167,139,250,0.85) !important;
    box-shadow: 0 10px 30px rgba(109,40,217,0.45);
}
div[data-testid="stPageLink"] a {
    justify-content: center !important;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f5f3ff !important;
}
div[data-testid="stPageLink"] a p {
    color: #f5f3ff !important;
    font-weight: 700;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stPageLink"]) .stCaption {
    text-align: center;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stPageLink"]) p {
    text-align: center;
    color: #a99bd4;
    font-size: 0.82rem;
}

.footer-note {
    text-align: center;
    color: #7a6aa0;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
    margin-top: 1.5rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Hero Section
# ---------------------------------------------------

st.markdown("""
<div class="hero-wrap">
    <div class="orb-stage">
        <div class="orb-ring"></div>
        <div class="orb-ring delay1"></div>
        <div class="orb-ring delay2"></div>
        <div class="orb-core"></div>
    </div>
    <h1 class="hero-title">FMCG Demand Forecasting</h1>
    <p class="hero-subtitle">AI-powered supply chain decisions — forecast demand, cut stockouts, plan smarter.</p>
    <p class="hero-meta">Live Data &nbsp;·&nbsp; Machine Learning &nbsp;·&nbsp; Real-Time Insights</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# KPI Cards
# ---------------------------------------------------

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card"><div class="kpi-label">Transactions</div><div class="kpi-value">{len(df):,}</div></div>
    <div class="kpi-card"><div class="kpi-label">Countries</div><div class="kpi-value">{kpis["Countries"]}</div></div>
    <div class="kpi-card"><div class="kpi-label">Cities</div><div class="kpi-value">{kpis["Cities"]}</div></div>
    <div class="kpi-card"><div class="kpi-label">Products</div><div class="kpi-value">{kpis["Products"]}</div></div>
    <div class="kpi-card"><div class="kpi-label">Revenue</div><div class="kpi-value">${df['net_sales'].sum():,.0f}</div></div>
    <div class="kpi-card"><div class="kpi-label">Units Sold</div><div class="kpi-value">{df['units_sold'].sum():,.0f}</div></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Overview + Stack
# ---------------------------------------------------

left, right = st.columns([2, 1])

with left:
    st.markdown('<div class="section-title">Project Objective</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="color:#d8cff2; font-size:0.95rem;">
    Forecasting engine for an FMCG retailer, combining <b>SQL + Machine Learning + BI dashboards</b>.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("""
<span class="tag">Forecast Demand</span>
<span class="tag">Reduce Stockouts</span>
<span class="tag">Optimise Inventory</span>
<span class="tag">Track Trends</span>
<span class="tag">Support Decisions</span>
""", unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">Tech Stack</div>', unsafe_allow_html=True)
    st.markdown("""
<span class="tag">Python</span>
<span class="tag">PostgreSQL</span>
<span class="tag">Plotly</span>
<span class="tag">Streamlit</span>
<span class="tag">Random Forest</span>
<span class="tag">Scikit-learn</span>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# Navigation — Application Modules
# ---------------------------------------------------

st.markdown('<div class="section-title">Explore the App</div>', unsafe_allow_html=True)

modules = [
    ("Dashboard", "Executive KPI overview", "pages/1_Dashboard.py"),
    ("Demand Forecast", "Predict future demand", "pages/2_Demand_Forecast.py"),
    ("Sales Analytics", "Revenue and sales trends", "pages/3_Sales_Analytics.py"),
    ("Inventory Analytics", "Stock levels and turnover", "pages/4_Inventory_Analytics.py"),
    ("Customer Market Analytics", "Customer and market segments", "pages/5_Customer_Market_Analytics.py"),
    ("Model Analytics", "Compare and interpret models", "pages/6_Model_Analytics.py"),
]

row1 = st.columns(3)
row2 = st.columns(3)
columns = row1 + row2

for col, (title, caption, page_path) in zip(columns, modules):
    with col:
        with st.container(border=True):
            st.page_link(page_path, label=title, use_container_width=True)
            st.caption(caption)

# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.markdown('<p class="footer-note">FMCG Global Demand Forecasting · Data Science Capstone Project</p>', unsafe_allow_html=True)