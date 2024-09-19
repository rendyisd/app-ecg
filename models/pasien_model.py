# import sqlite3
import re

from controllers.database import Database

class Pasien:
    def __init__(self, id=None, nama=None):
        self.id = id
        self.nama = nama

    @staticmethod
    def validate(nama):
        if not nama:
            return False, "'nama' tidak boleh kosong."
        if len(nama) < 2 or len(nama) > 64:
            return False, "Panjang 'nama' harus 2 hingga 64 karakter."
        if not re.match(r'^[a-zA-Z\s\-]+$', nama):
            return False, "'nama' hanya boleh berisi huruf dan spasi."
        return True, ""

    @staticmethod
    def create(nama):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO pasien (nama) VALUES (?)", (nama,))
        conn.commit()
        return Pasien(id=cursor.lastrowid, nama=nama)

    @staticmethod
    def get_by_id(id):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pasien WHERE id = ?", (id,))

        row = cursor.fetchone()

        if row:
            return Pasien(id=row[0], nama=row[1])
        return None
    
    @staticmethod
    def get_all():
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pasien")

        rows = cursor.fetchall()
        return [Pasien(id=row[0], nama=row[1]) for row in rows]

    def update(self, new_nama):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE pasien SET nama = ? WHERE id = ?", (new_nama, self.id))
        self.nama = new_nama

        conn.commit()
    
    def delete(self):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM pasien WHERE id = ?", (self.id,))
        conn.commit()
        

    def __repr__(self):
        return f"<Pasien(id={self.id}, nama={self.nama})>"