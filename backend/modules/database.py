import sqlite3
DB_PATH = "stock_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS stocks (symbol TEXT PRIMARY KEY, name TEXT, sector TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS swot_reports (symbol TEXT PRIMARY KEY, swot_data TEXT, created_at TEXT)")
    cursor.execute("INSERT OR IGNORE INTO stocks VALUES ('RELIANCE', 'Reliance Industries', 'Oil & Gas'), ('TCS', 'TCS', 'IT'), ('HDFCBANK', 'HDFC Bank', 'Banking')")
    conn.commit()
    conn.close()
    print("Database initialized")
