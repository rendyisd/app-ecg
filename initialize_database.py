import sqlite3
from controllers.database import Database

def initialize_db():
    conn = Database.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_result (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            lead VARCHAR(8) NOT NULL,
            dirname VARCHAR(255) NOT NULL,
            denoised_data TEXT NOT NULL, -- array as JSON
            delineation_result TEXT NOT NULL, -- array as JSON
            detection_result TEXT NOT NULL, -- array of integers as JSON, 1 integer represents 1 beat detection result
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(record_id) REFERENCES record(id)
        )
    """)

    conn.commit()
    Database.close_db_connection()

def seed_db():
    conn = Database.get_db_connection()
    cursor = conn.cursor()

    records = [
        ("john doe",),
        ("jane doe",),
        ("joni joni",),
        ("yes papa",),
        ("budi arie",)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO record (name)
        VALUES (?)
    """, records)

    cursor.execute("SELECT * FROM record")
    rows = cursor.fetchall()

    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, created_at: {row[2]}")

    conn.commit()
    Database.close_db_connection()

def main():
    initialize_db()
    # seed_db()

if __name__ == "__main__":
    main() 