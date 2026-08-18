import calendar
import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        today = date.today()
        _, days_in_month = calendar.monthrange(today.year, today.month)

        sample_expenses = [
            # (amount, category, day, description)
            (54.32, "Food", 2, "Grocery shopping"),
            (45.00, "Transport", 5, "Monthly metro pass"),
            (120.75, "Bills", 7, "Electricity bill"),
            (32.50, "Health", 10, "Pharmacy - vitamins"),
            (28.00, "Entertainment", 12, "Movie tickets"),
            (89.99, "Shopping", 15, "New running shoes"),
            (15.40, "Other", 18, "Miscellaneous purchase"),
            (62.10, "Food", 22, "Dinner with friends"),
        ]

        for amount, category, day, description in sample_expenses:
            expense_date = date(today.year, today.month, min(day, days_in_month)).isoformat()
            conn.execute(
                """INSERT INTO expenses (user_id, amount, category, date, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, amount, category, expense_date, description),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email):
    """Expects `email` to already be normalized (trimmed, lowercased) by the caller."""
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()
    return user


def create_user(name, email, password):
    conn = get_db()
    try:
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        user_id = cursor.lastrowid
    finally:
        conn.close()
    return user_id
