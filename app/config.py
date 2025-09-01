import os

# Database URL (SQLite in /data directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "accountability.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
