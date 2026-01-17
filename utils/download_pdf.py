
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd

def generate_pdf(df: pd.DataFrame) -> str:
    path = "compliance_report.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    x, y = 40, height - 40
    c.setFont("Helvetica", 9)

    c.drawString(x, y, "Compliance Report")
    y -= 20

    headers = df.columns.tolist()
    c.drawString(x, y, " | ".join(headers))
    y -= 15

    for _, row in df.iterrows():
        line = " | ".join(str(v) for v in row.values)
        c.drawString(x, y, line[:100])
        y -= 12
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 9)
            y = height - 40

    c.save()
    return path
