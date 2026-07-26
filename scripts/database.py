import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

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

print("Database Connected Successfully")