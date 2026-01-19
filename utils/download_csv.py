import pandas as pd
import tempfile
import os


def generate_csv(df: pd.DataFrame):
    """
    Generates CSV directly from the UI DataFrame.
    Guarantees exported CSV == UI table.
    """

    if df is None or df.empty:
        return None

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "compliance_report.csv")

    # ✅ Preserve UI formatting exactly
    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8",
        line_terminator="\n"
    )

    return file_path
