import sqlite3

conn = sqlite3.connect("test.db")

c = conn.cursor()

query = """
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
"""

c.execute(query)

conn.close()