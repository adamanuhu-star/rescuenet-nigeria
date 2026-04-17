import sqlite3

conn = sqlite3.connect("rescuenet.db", check_same_thread=False)
c = conn.cursor()

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

# REPORTS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident TEXT,
    agency TEXT,
    description TEXT,
    lat REAL,
    lon REAL,
    user TEXT,
    time TEXT
)
""")

conn.commit()
