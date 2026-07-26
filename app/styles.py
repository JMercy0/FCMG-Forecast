import streamlit as st


def load_css():
    """Inject the global animated purple theme. Call once at the top of every page."""

    st.markdown("""
    <style>

    /* ---------------------------------------------------
       Keyframes
    --------------------------------------------------- */

    @keyframes bgPulse {
        0%   { background-position: 50% 50%; }
        50%  { background-position: 50% 60%; }
        100% { background-position: 50% 50%; }
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes glowPulse {
        0%   { box-shadow: 0 0 0 rgba(139,92,246,0); }
        50%  { box-shadow: 0 0 18px rgba(139,92,246,0.35); }
        100% { box-shadow: 0 0 0 rgba(139,92,246,0); }
    }

    /* ---------------------------------------------------
       App background
    --------------------------------------------------- */

    .stApp {
        background: radial-gradient(circle at 50% 30%, #3b2478 0%, #241457 35%, #140b33 70%, #0a0620 100%);
        background-size: 140% 140%;
        animation: bgPulse 16s ease-in-out infinite;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c1044 0%, #140b33 100%);
        border-right: 1px solid rgba(167,139,250,0.15);
    }

    /* Top header bar */
    header[data-testid="stHeader"] {
        background: linear-gradient(180deg, #241457 0%, #140b33 100%);
        border-bottom: 1px solid rgba(167,139,250,0.15);
    }
    header[data-testid="stHeader"] * {
        color: #f5f3ff !important;
    }

    /* Sidebar navigation links (page names) */
    section[data-testid="stSidebarNav"] a,
    section[data-testid="stSidebarNav"] span,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li {
        color: #f5f3ff !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebarNav"] a:hover {
        background: rgba(139,92,246,0.18) !important;
        border-radius: 8px;
    }

    /* Active/selected page link */
    section[data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(139,92,246,0.3) !important;
        border-radius: 8px;
        border-left: 3px solid #a78bfa;
    }
    section[data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* ---------------------------------------------------
       Headings & text
    --------------------------------------------------- */

    h1, h2, h3 {
        color: #ffffff !important;
        text-shadow: 0 0 18px rgba(255,255,255,0.25), 0 0 40px rgba(167,139,250,0.4);
        animation: fadeUp 0.6s ease-out;
    }

    h4, h5, h6, p, label, .stMarkdown {
        color: #e4d9ff;
    }

    /* ---------------------------------------------------
       Page header helper (used via utils.page_header)
    --------------------------------------------------- */

    .page-header {
        padding: 1.6rem 1.5rem;
        border-radius: 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(167,139,250,0.25);
        margin-bottom: 1.5rem;
        animation: fadeUp 0.6s ease-out;
    }
    .page-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    .page-header p {
        margin-top: 0.4rem;
        color: #b8a9e0;
    }

    /* ---------------------------------------------------
       Metrics (st.metric)
    --------------------------------------------------- */

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 14px;
        padding: 1rem 0.8rem;
        backdrop-filter: blur(6px);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(167,139,250,0.7);
        box-shadow: 0 8px 24px rgba(109,40,217,0.35);
    }
    div[data-testid="stMetricLabel"] {
        color: #a99bd4 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.72rem !important;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 700;
    }

    /* ---------------------------------------------------
       Buttons
    --------------------------------------------------- */

    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #6d28d9, #8b5cf6);
        color: #ffffff;
        border: none;
        border-radius: 22px;
        padding: 0.5rem 1.4rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.25s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        animation: glowPulse 1.4s ease-in-out infinite;
        transform: translateY(-2px);
    }

    /* ---------------------------------------------------
       Inputs / selectboxes
    --------------------------------------------------- */

    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stDateInput > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(167,139,250,0.35) !important;
        border-radius: 10px !important;
        color: #f5f3ff !important;
    }

    /* ---------------------------------------------------
       Alerts (info / success / warning / error)
    --------------------------------------------------- */

    div[data-testid="stAlert"] {
        border-radius: 12px;
        border: 1px solid rgba(167,139,250,0.3);
        backdrop-filter: blur(6px);
    }

    /* ---------------------------------------------------
       Dataframes / tables
    --------------------------------------------------- */

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 12px;
        overflow: hidden;
    }

    /* ---------------------------------------------------
       Dividers
    --------------------------------------------------- */

    hr {
        border-color: rgba(167,139,250,0.25) !important;
    }

    /* ---------------------------------------------------
       Reusable component classes (cards, tags, orb)
       — available to any page that wants them
    --------------------------------------------------- */

    .glass-card {
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 14px;
        padding: 1.4rem 1rem;
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(6px);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(167,139,250,0.85);
        box-shadow: 0 10px 30px rgba(109,40,217,0.45);
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

    </style>
    """, unsafe_allow_html=True)