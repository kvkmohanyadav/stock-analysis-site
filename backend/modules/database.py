import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
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
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT,
            created_at TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # Create password tokens table for password reset and creation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            token_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0
        )
    """)
    
    # Create default admin user if it doesn't exist
    admin_password_hash = hashlib.sha256("password".encode()).hexdigest()
    cursor.execute("""
        INSERT OR IGNORE INTO users (first_name, last_name, email, phone, password_hash, created_at)
        VALUES ('Admin', 'User', 'admin@stockanalysis.com', '', ?, ?)
    """, (admin_password_hash, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print("Database initialized")
