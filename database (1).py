"""
database.py
------------
All SQLite database logic for MindCare AI lives here.
Using SQLite keeps setup dead simple (no server needed) while still giving
every user persistent history for mood logs, journal entries, and chats.
"""

import sqlite3
import hashlib
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(__file__), "mindcare.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            sentiment_label TEXT,
            sentiment_score REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            sentiment_label TEXT,
            sentiment_score REAL,
            is_crisis_flag INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS calorie_profile (
            user_id INTEGER PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            activity_level TEXT,
            bmr REAL,
            tdee REAL,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


# ---------- Auth helpers ----------

def _hash_password(password: str) -> str:
    salt = "mindcare_static_salt"  # simple demo salt; use per-user salt in production
    return hashlib.sha256((salt + password).encode()).hexdigest()


def create_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username.strip(), _hash_password(password), datetime.now().isoformat()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def verify_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    row = cur.fetchone()
    conn.close()
    if row and row["password_hash"] == _hash_password(password):
        return dict(row)
    return None


# ---------- Mood log helpers ----------

def add_mood_log(user_id: int, mood_score: int, note: str, log_date: str = None):
    conn = get_connection()
    cur = conn.cursor()
    log_date = log_date or date.today().isoformat()
    cur.execute(
        "INSERT INTO mood_logs (user_id, log_date, mood_score, note, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, log_date, mood_score, note, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_mood_logs(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM mood_logs WHERE user_id = ? ORDER BY log_date ASC", (user_id,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------- Journal helpers ----------

def add_journal_entry(user_id: int, title: str, content: str, sentiment_label: str, sentiment_score: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO journal_entries
           (user_id, title, content, sentiment_label, sentiment_score, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, title, content, sentiment_label, sentiment_score, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_journal_entries(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM journal_entries WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------- Chat helpers ----------

def add_chat_message(user_id: int, role: str, message: str,
                      sentiment_label: str = None, sentiment_score: float = None,
                      is_crisis_flag: bool = False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO chat_history
           (user_id, role, message, sentiment_label, sentiment_score, is_crisis_flag, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, role, message, sentiment_label, sentiment_score,
         int(is_crisis_flag), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id: int, limit: int = 50):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at ASC LIMIT ?",
        (user_id, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------- Calorie profile helpers ----------

def upsert_calorie_profile(user_id: int, age, gender, height_cm, weight_kg,
                            activity_level, bmr, tdee):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO calorie_profile
               (user_id, age, gender, height_cm, weight_kg, activity_level, bmr, tdee, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               age=excluded.age, gender=excluded.gender, height_cm=excluded.height_cm,
               weight_kg=excluded.weight_kg, activity_level=excluded.activity_level,
               bmr=excluded.bmr, tdee=excluded.tdee, updated_at=excluded.updated_at""",
        (user_id, age, gender, height_cm, weight_kg, activity_level, bmr, tdee,
         datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_calorie_profile(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM calorie_profile WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
