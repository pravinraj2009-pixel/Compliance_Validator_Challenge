
import sqlite3

def get_conn(path):
    conn = sqlite3.connect(path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS decisions (
            invoice_id TEXT,
            decision TEXT,
            confidence REAL
        )"""
    )
    return conn
