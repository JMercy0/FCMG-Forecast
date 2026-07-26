from pathlib import Path

# ============================================
# Project Directories
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
APP_DIR = PROJECT_ROOT / "app"
ASSETS_DIR = APP_DIR / "assets"

# ============================================
# Files
# ============================================

DATA_FILE = DATA_DIR / "processed" / "fmcg_sales_clean.csv"

MODEL_FILE = MODEL_DIR / "fmcg_forecasting_model.pkl"

LOGO_FILE = ASSETS_DIR / "logo.png"

BANNER_FILE = ASSETS_DIR / "banner.png"