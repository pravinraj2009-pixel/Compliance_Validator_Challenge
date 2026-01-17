
import pandas as pd

def generate_csv(df: pd.DataFrame) -> str:
    path = "compliance_report.csv"
    df.to_csv(path, index=False)
    return path
