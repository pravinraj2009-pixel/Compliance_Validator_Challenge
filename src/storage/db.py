<<<<<<< HEAD
import sqlite3

def get_conn(path):
    # Thread-safe connection (required for parallel execution)
    conn = sqlite3.connect(
        path,
        check_same_thread=False
    )

    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            invoice_id TEXT,
            decision TEXT,
            confidence REAL
        )
        """
    )

    # 🚀 CRITICAL PERFORMANCE INDEX
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_decisions_invoice_id
        ON decisions (invoice_id)
        """
    )

    conn.commit()
=======

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
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    return conn
