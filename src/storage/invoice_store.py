
from src.storage.db import get_conn

class InvoiceStore:
    def __init__(self, db_path):
        self.conn = get_conn(db_path)

    def is_duplicate(self, invoice_id):
        cur = self.conn.execute(
            "SELECT COUNT(*) FROM decisions WHERE invoice_id=?",
            (invoice_id,)
        )
        return cur.fetchone()[0] > 0

    def record(self, invoice_id):
        self.conn.execute(
            "INSERT INTO decisions VALUES (?, ?, ?)",
            (invoice_id, "SEEN", 0.0)
        )
        self.conn.commit()
