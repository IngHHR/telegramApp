import sqlite3
from datetime import datetime

DB_NAME = "db.sqlite"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Crear tabla de tareas
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            created_at TEXT
        )
    """)

    # Crear tabla de notas
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            created_at TEXT
        )
    """)

    # Crear tabla de gastos
    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            note TEXT,
            created_at TEXT
        )
    """)

    # Crear tabla de recordatorios con chat_id
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            message TEXT NOT NULL,
            chat_id INTEGER NOT NULL,
            sent INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def add_task(text):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO tasks (text, created_at) VALUES (?, ?)",
            (text, datetime.now().strftime('%Y-%m-%d %H:%M'))
        )

def list_tasks():
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute("SELECT id, text FROM tasks").fetchall()

def add_note(text):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)",
            (text, datetime.now().strftime('%Y-%m-%d %H:%M'))
        )

def add_expense(amount, category, note):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, note, created_at) VALUES (?, ?, ?, ?)",
            (amount, category, note, datetime.now().strftime('%Y-%m-%d %H:%M'))
        )

def save_reminder(datetime_str, message, chat_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO reminders (datetime, message, chat_id) VALUES (?, ?, ?)",
            (datetime_str, message, chat_id)
        )

def get_due_reminders():
    with sqlite3.connect(DB_NAME) as conn:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        return conn.execute(
            "SELECT id, message, chat_id FROM reminders WHERE datetime <= ? AND sent = 0",
            (now,)
        ).fetchall()

def mark_reminder_sent(reminder_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))
