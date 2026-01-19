import tempfile
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def generate_pdf(df):
    """
    Generates a professional PDF report directly
    from the UI DataFrame.
    """

    if df is None or df.empty:
        return None

    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "compliance_report.pdf")

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=24,
        leftMargin=24,
        topMargin=24,
        bottomMargin=24,
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------------------------------
    # Title
    # -------------------------------------------------
    elements.append(
        Paragraph(
            "<b>Agentic AI Compliance Validation Report</b>",
            styles["Title"]
        )
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    # -------------------------------------------------
    # Prepare table data
    # -------------------------------------------------
    table_data = []

    # Header row
    table_data.append(list(df.columns))

    # Data rows (wrap text)
    for _, row in df.iterrows():
        wrapped_row = []
        for cell in row:
            text = "" if cell is None else str(cell).replace("\n", "<br/>")
            wrapped_row.append(Paragraph(text, styles["Normal"]))
        table_data.append(wrapped_row)

    # -------------------------------------------------
    # Build table
    # -------------------------------------------------
    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[70] * len(df.columns)
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(table)

    # -------------------------------------------------
    # Build PDF
    # -------------------------------------------------
    doc.build(elements)

    return file_path
