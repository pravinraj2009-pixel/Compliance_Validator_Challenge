import pandas as pd
import tempfile
import os
<<<<<<< HEAD
from datetime import datetime
=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6


def generate_csv(df: pd.DataFrame):
    """
<<<<<<< HEAD
    Generates a clean, Excel-friendly CSV
    that exactly matches the UI table.
=======
    Generates CSV directly from the UI DataFrame.
    Guarantees exported CSV == UI table.
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    """

    if df is None or df.empty:
        return None

    temp_dir = tempfile.mkdtemp()
<<<<<<< HEAD
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(
        temp_dir, f"compliance_report_{timestamp}.csv"
    )

    # -------------------------------------------------
    # Metadata header (human-friendly)
    # -------------------------------------------------
    meta_rows = [
        ["Report Name", "Agentic AI Compliance Validation Report"],
        ["Generated On", datetime.now().strftime("%d %b %Y, %H:%M:%S")],
        ["Total Records", len(df)],
        [],
    ]

    df_meta = pd.DataFrame(meta_rows)

    # Combine metadata + data
    final_df = pd.concat([df_meta, df], ignore_index=True)

    # -------------------------------------------------
    # Write CSV (Excel safe)
    # -------------------------------------------------
    final_df.to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig",   # Excel UTF-8
        lineterminator="\n"
=======
    file_path = os.path.join(temp_dir, "compliance_report.csv")

    # ✅ Preserve UI formatting exactly
    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8",
        line_terminator="\n"
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    )

    return file_path
