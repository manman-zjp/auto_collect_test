# auto_collect/crawler/storage.py
import sqlite3

DB_FILE = "results.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT,
        link TEXT UNIQUE,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    return conn

def save_link(conn, keyword, link, source):
    try:
        conn.execute(
            "INSERT INTO links (keyword, link, source) VALUES (?, ?, ?)",
            (keyword, link, source)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # 已存在就跳过
        pass

def fetch_all(conn):
    c = conn.cursor()
    c.execute("SELECT keyword, link, source, created_at FROM links ORDER BY created_at DESC")
    return c.fetchall()