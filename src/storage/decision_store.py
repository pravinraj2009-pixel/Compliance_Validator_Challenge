<<<<<<< HEAD
from src.storage.db import get_conn
import threading

class DecisionStore:
    _lock = threading.Lock()

    def __init__(self, db_path):
        self.db_path = db_path

    def log_decision(self, invoice_id, decision, confidence):
        # Open-per-write is safer + faster under threads
        with self._lock:
            conn = get_conn(self.db_path)
            conn.execute(
                """
                INSERT INTO decisions (invoice_id, decision, confidence)
                VALUES (?, ?, ?)
                """,
                (invoice_id, decision, confidence)
            )
            conn.close()
=======

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
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
