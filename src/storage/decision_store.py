
from src.storage.db import get_conn

class DecisionStore:
    def __init__(self, db_path):
        self.conn = get_conn(db_path)
        self.db_path = db_path

    def log_decision(self, invoice_id, decision, confidence):
        self.conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?)",
            (invoice_id, decision, confidence)
        )
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Cleanup: close connection when object is destroyed."""
        try:
            self.close()
        except:
            pass
