
from src.storage.db import get_conn

class DecisionStore:
    def __init__(self, db_path):
        self.conn = get_conn(db_path)

    def log_decision(self, invoice_id, decision, confidence):
        self.conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?)",
            (invoice_id, decision, confidence)
        )
        self.conn.commit()
