import os
import time

import pandas as pd
from tqdm import tqdm
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ==========================================
# Load Environment Variables
# ==========================================

load_dotenv()

USERNAME = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

engine = create_engine(DATABASE_URL)

# ==========================================
# Configuration
# ==========================================

CSV_FILE = "data/raw/fmcg_sales_3years_1M_rows.csv"
TABLE_NAME = "fmcg_sales"
CHUNK_SIZE = 50000

# ==========================================
# Verify CSV Exists
# ==========================================

if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"Cannot find: {CSV_FILE}")

print("CSV found.")