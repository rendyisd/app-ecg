import json

from controllers.database import Database

class DetectionResult:
    def __init__(self, id, record, lead, dirname, denoised_data, delineation_result, detection_result):
        self.id = id
        self.record = record
        self.lead = lead
        self.dirname = dirname
        self.denoised_data = denoised_data
        self.delineation_result = delineation_result
        self.detection_result = detection_result

    @staticmethod
    def create(record, lead, dirname, denoised_data, delineation_result, detection_result):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        record_id = record.id
        str_denoised_data = json.dumps(denoised_data)
        str_delineation_result = json.dumps(delineation_result)
        str_detection_result = json.dumps(detection_result)

        cursor.execute("""
            INSERT INTO detection_result (record_id, lead, dirname, denoised_data, delineation_result, detection_result)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
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
            record,
            lead,
            dirname,
            denoised_data,
            delineation_result,
            detection_result
        )
    
    @staticmethod
    def get_by_record(record):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detection_result WHERE record_id = ?", (record.id,))

        rows = cursor.fetchall()

        return [DetectionResult(
            id=row[0],
            record=record,
            lead=row[2],
            dirname=row[3],
            denoised_data=json.loads(row[4]),
            delineation_result=json.loads(row[5]),
            detection_result=json.loads(row[6])
        ) for row in rows]
    
    @staticmethod
    def get_by_record_lead(record, lead):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detection_result WHERE record_id = ? AND lead = ?", (record.id, lead))

        row = cursor.fetchone()

        if row:
            return DetectionResult(
                id=row[0],
                record=record,
                lead=lead,
                dirname=row[3],
                denoised_data=json.loads(row[4]),
                delineation_result=json.loads(row[5]),
                detection_result=json.loads(row[6])
            )
        return None

    @staticmethod
    def get_by_id(id):
        from models.record_model import Record
        
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM detection_result WHERE id = ?", (id,))

        row = cursor.fetchone()

        if row:
            return DetectionResult(
                id=row[0],
                record=Record.get_by_id(row[1]),
                lead=row[2],
                dirname=row[3],
                denoised_data=json.loads(row[4]),
                delineation_result=json.loads(row[5]),
                detection_result=json.loads(row[6])
            )
        return None
    
    def delete(self):
        conn = Database.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM detection_result WHERE id = ?", (self.id,))

        other_results = DetectionResult.get_by_record(self.record)

        if not other_results:
            self.record.delete()

        conn.commit()

    def __repr__(self) -> str:
        return f"""
        <DetectionResult(
            id={self.id},
            record={self.record},
            lead={self.lead},
            dirname={self.dirname},
            denoised_data=...,
            delineation_result=...,
            detection_result=...
        )>
        """