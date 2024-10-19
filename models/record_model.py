# import sqlite3
import re

from controllers.database import Database

class Record:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    # @staticmethod
    # def validate(name):
    #     if not name:
    #         return False, "'name' tidak boleh kosong."
    #     if len(name) < 2 or len(name) > 64:
    #         return False, "Panjang 'name' harus 2 hingga 64 karakter."
    #     if not re.match(r'^[a-zA-Z\s\-]+$', name):
    #         return False, "'name' hanya boleh berisi huruf dan spasi."
    #     return True, ""

    @staticmethod
    def create(name):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO record (name) VALUES (?)", (name,))
        conn.commit()
        return Record(id=cursor.lastrowid, name=name)

    @staticmethod
    def get_by_id(id):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM record WHERE id = ?", (id,))

        row = cursor.fetchone()

        if row:
            return Record(id=row[0], name=row[1])
        return None
    
    @staticmethod
    def get_by_name(name):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM record WHERE name = ?", (name,))

        row = cursor.fetchone()

        if row:
            return Record(id=row[0], name=row[1])
        return None
    
    @staticmethod
    def get_or_create(name):
        record = Record.get_by_name(name)

        if record:
            return record
        else:
            return Record.create(name)
    
    @staticmethod
    def get_all():
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM record")

        rows = cursor.fetchall()
        return [Record(id=row[0], name=row[1]) for row in rows]

    def update(self, new_name):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE record SET name = ? WHERE id = ?", (new_name, self.id))
        self.name = new_name

        conn.commit()
    
    def delete(self):
        from models.detection_result_model import DetectionResult

        conn = Database.get_db_connection()
        cursor = conn.cursor()

        results = DetectionResult.get_by_record(self)

        for result in results:
            result.delete()

        cursor.execute("DELETE FROM record WHERE id = ?", (self.id,))
        conn.commit()
        

    def __repr__(self):
        return f"<record(id={self.id}, name={self.name})>"