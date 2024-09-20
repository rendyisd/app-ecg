import json

from controllers.database import Database
from models.pasien_model import Pasien

class DetectionResult:
    def __init__(self, id, pasien, lead, dirname, denoised_data, delineation_result, detection_result):
        self.id = id
        self.pasien = pasien
        self.lead = lead
        self.dirname = dirname
        self.denoised_data = denoised_data
        self.delineation_result = delineation_result
        self.detection_result = detection_result

    @staticmethod
    def create(pasien, lead, dirname, denoised_data, delineation_result, detection_result):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        pasien_id = pasien.id
        str_denoised_data = json.dumps(denoised_data)
        str_delineation_result = json.dumps(delineation_result)
        str_detection_result = json.dumps(detection_result)

        cursor.execute("""
            INSERT INTO detection_result (pasien_id, lead, dirname, denoised_data, delineation_result, detection_result)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                pasien_id,
                lead,
                dirname,
                str_denoised_data,
                str_delineation_result,
                str_detection_result,
            )
        )

        conn.commit()

        return DetectionResult(
            cursor.lastrowid,
            pasien,
            lead,
            dirname,
            denoised_data,
            delineation_result,
            detection_result
        )
    
    @staticmethod
    def get_by_pasien(pasien):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detection_result WHERE pasien_id = ?", (pasien.id,))

        rows = cursor.fetchall()

        return [DetectionResult(
            id=row[0],
            pasien=pasien,
            lead=row[2],
            dirname=row[3],
            denoised_data=json.loads(json.loads(row[4])),
            delineation_result=json.loads(json.loads(row[5])),
            detection_result=json.loads(json.loads(row[6]))
        ) for row in rows]

    @staticmethod
    def get_by_id(id):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detection_result WHERE id = ?", (id,))

        row = cursor.fetchone()

        if row:
            return DetectionResult(
                id=row[0],
                pasien=Pasien.get_by_id(row[1]),
                lead=row[2],
                dirname=row[3],
                denoised_data=json.loads(json.loads(row[4])),
                delineation_result=json.loads(json.loads(row[5])),
                detection_result=json.loads(json.loads(row[6]))
            )
        return None

    def __repr__(self) -> str:
        return f"""
        <DetectionResult(
            id={self.id},
            pasien={self.pasien},
            lead={self.lead},
            dirname={self.dirname},
            denoised_data=...,
            delineation_result=...,
            detection_result=...
        )>
        """