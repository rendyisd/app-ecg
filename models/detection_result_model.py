import json

from controllers.database import Database

class DetectionResult:
    def __init__(self, id, pasien, lead, filepath, denoised_data, delineation_result, detection_result):
        self.id = id
        self.pasien = pasien
        self.lead = lead
        self.filepath = filepath
        self.denoised_data = denoised_data
        self.delineation_result = delineation_result
        self.detection_result = detection_result

    @staticmethod
    def create(pasien, lead, filepath, denoised_data, delineation_result, detection_result):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        pasien_id = pasien.id
        str_denoised_data = json.dumps(denoised_data)
        str_delineation_result = json.dumps(delineation_result)
        str_detection_result = json.dumps(detection_result)

        cursor.execute("""
            INSERT INTO detection_result (pasien_id, lead, filepath, denoised_data, delineation_result, detection_result)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            pasien_id,
            lead,
            filepath,
            str_denoised_data,
            str_delineation_result,
            str_detection_result
        )

        conn.commit()

        return DetectionResult(
            cursor.lastrowid,
            pasien,
            lead,
            filepath,
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
            filepath=row[3],
            denoised_data=json.loads(row[4]),
            delineation_result=json.loads(row[5]),
            detection_result=json.loads(row[6])
        ) for row in rows]