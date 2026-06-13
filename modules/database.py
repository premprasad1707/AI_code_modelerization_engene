import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path('data/migration_history.db')


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_code TEXT NOT NULL,
            migrated_code TEXT NOT NULL,
            issue_count INTEGER,
            risk_score REAL,
            risk_level TEXT,
            suggestions TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


def insert_migration(filename, original_code, migrated_code, issue_count, risk_score, risk_level, suggestions):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO migrations
        (filename, original_code, migrated_code, issue_count, risk_score, risk_level, suggestions, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        filename,
        original_code,
        migrated_code,
        issue_count,
        risk_score,
        risk_level,
        suggestions,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    conn.commit()
    conn.close()


def fetch_history():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, filename, issue_count, risk_score, risk_level, created_at FROM migrations ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_full_record(record_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM migrations WHERE id = ?', (record_id,))
    row = cur.fetchone()
    conn.close()
    return row
