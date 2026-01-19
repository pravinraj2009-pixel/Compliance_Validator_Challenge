import pandas as pd
import gradio as gr

from src.orchestration.compliance_pipeline import run_compliance_pipeline
from src.config import load_config

from utils.download_csv import generate_csv
from utils.download_pdf import generate_pdf


# =========================================================
# TABLE CONFIGURATION
# =========================================================

TABLE_COLUMN_LABELS = [
    "Invoice ID",
    "Compliance\nDecision",
    "Confidence\nScore",
    "Primary Reason",
    "Decision Rationale",
    "Escalation\nRequired",
    "Failed Checks",
    "Review Flags",
    "Conflicts Identified",
]


TABLE_COLUMNS = [
    "invoice_id",
    "decision",
    "final_confidence",
    "primary_reason",
    "decision_rationale",
    "escalation_required",
    "failed_checks",
    "review_flags",
    "conflicts",
]


# =========================================================
# VALIDATION CODE → User Friendly text
# =========================================================

VALIDATION_TEXT_MAP = {
    "B1": "Invalid GSTIN format",
    "B2": "GSTIN suspended or not registered",
    "B3": "Seller state information missing",
    "B8": "Insufficient data to determine tax type",
    "B12": "E-invoice required but IRN missing",
    "B15": "E-invoice required but IRN missing",
    "D1": "TDS applicability needs confirmation",
    "D3": "PAN not available – higher TDS applicable",
    "D5": "TDS threshold validation passed",
    "D7": "TDS on GST component handled correctly",
    "D9": "TAN not configured",
}


def resolve_validation_text(code: str) -> str:
    """
    Guarantees readable validation text even if a new
    rule code is introduced without UI mapping.
    """
    return VALIDATION_TEXT_MAP.get(
        code,
        f"Validation rule {code} failed"
    )


# =========================================================
# PIPELINE EXECUTION + NORMALIZATION
# =========================================================

def run_pipeline(show_only_escalated: bool):
    """
    Executes the compliance pipeline and prepares
    data for UI consumption.
    """

    # -----------------------------------------------------
    # Load configuration
    # -----------------------------------------------------
    config = load_config()

    # -----------------------------------------------------
    # Run pipeline
    # -----------------------------------------------------
    summary, reports = run_compliance_pipeline(
        config,
        force_run=True
    )

    # -----------------------------------------------------
    # Initialize aggregation
    # -----------------------------------------------------
    rows = []
    escalation_count = 0
    llm_reasoning = []

    # -----------------------------------------------------
    # Process each invoice report
    # -----------------------------------------------------
    for r in reports:

        is_escalated = bool(r.get("escalation_required"))

        if is_escalated:
            escalation_count += 1

        decision = r.get("decision", "")

        # -------------------------------------------------
        # Decision rationale
        # -------------------------------------------------
        if decision == "ESCALATE":
            rationale = "One or more critical compliance failures detected"
        elif decision == "APPROVE_WITH_REVIEW":
            rationale = "Approved with non-blocking compliance ambiguity"
        elif decision == "APPROVE":
            rationale = "All compliance checks passed"
        else:
            rationale = "Decision pending review"

        # -------------------------------------------------
        # SAFE LIST HANDLING
        # -------------------------------------------------
        failed_checks = r.get("failed_checks") or []
        review_flags = r.get("review_flags") or []
        conflicts = r.get("conflicts") or []

        # -------------------------------------------------
        # Build table row
        # -------------------------------------------------
        rows.append({
            "invoice_id": r.get("invoice_id", ""),
            "decision": decision,
            "final_confidence": (
                f"{round(float(r.get('final_confidence', 0)) * 100)}%"
                if r.get("final_confidence") is not None else ""
            ),
            "primary_reason": r.get("primary_reason", ""),
            "decision_rationale": rationale,
            "escalation_required": "Yes" if is_escalated else "No",

            "failed_checks": "\n".join(
                resolve_validation_text(code)
                for code in failed_checks
            ),
            "review_flags": "\n".join(
                resolve_validation_text(code)
                for code in review_flags
            ),
            "conflicts": "\n".join(conflicts),
        })

    # -------------------------------------------------
    # Capture FIRST escalation explanation
    # -------------------------------------------------
    for r in reports:
        if r.get("escalation_required") and r.get("conflicts"):
            llm_reasoning = r.get("conflicts") or []
            break

    # -----------------------------------------------------
    # Create DataFrame
    # -----------------------------------------------------
    df = pd.DataFrame(rows, columns=TABLE_COLUMNS)
    df.columns = TABLE_COLUMN_LABELS

    # -----------------------------------------------------
    # Filtering
    # -----------------------------------------------------
    if show_only_escalated:
        df = df[df["Escalation\nRequired"] == "Yes"]

    # -----------------------------------------------------
    # Summary calculations
    # -----------------------------------------------------
    approved = len(reports) - escalation_count

    summary_text = f"""
**Total Invoices:** {len(reports)}  
**Approved Invoices:** {approved}  
**Escalated Invoices:** {escalation_count}  
**Processing Time (seconds):** {summary.get("processing_time_sec")}
"""

    escalation_msg = (
        "There are 0 escalated invoices."
        if escalation_count == 0
        else ""
    )

    return (
        summary_text,
        df,
        escalation_count,
        escalation_msg,
        llm_reasoning
    )


# =========================================================
# UI DEFINITION
# =========================================================

def launch_ui():

    with gr.Blocks(
        title="Agentic AI Compliance Validator"
    ) as app:

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------
        gr.HTML(
            """
            <div class="navbar">
                <div>
                    <h2>🧾 Agentic AI Compliance Validator</h2>
                    <div class="subtitle">
                        Automated invoice compliance review using explainable multi-agent intelligence
                    </div>
                </div>
                <div class="nav-links">
                    <a href="/file=text/Compliance%20Validator%20System%20Architecture%20Document.docx"
                    target="_blank">Architecture</a>

                    <a href="/file=docs/Compliance%20Validator%20System_Dry_Run_Walkthrough.docx"
                    target="_blank">Walkthrough</a>

                    <a href="/file=README.md"
                    target="_blank">README</a>
                </div>

            </div>
            """
        )

        # -------------------------------------------------
        # TABS
        # -------------------------------------------------
        with gr.Tabs():

            with gr.Tab("Overview"):
                gr.Markdown(
                    """
                    ### 📌 System Overview

                    This system implements an **agentic AI–based Accounts Payable compliance engine**.

                    - Deterministic GST, TDS, and policy validations  
                    - Human-in-the-loop escalation for ambiguity  
                    - Explainable, audit-ready decisions  
                    """
                )

            with gr.Tab("Agent Architecture"):
                gr.Markdown(
                    """
                    ### 🧠 Agent Architecture

                    **Extractor Agent**  
                    Normalizes incoming invoice data

                    **Validator Agents**  
                    Perform rule-based GST, TDS, and policy checks

                    **Resolver Agent**  
                    Handles ambiguity and conflicts

                    **Reporter Agent**  
                    Produces structured compliance reports
                    """
                )

            with gr.Tab("Audit & Traceability"):
                gr.Markdown(
                    """
                    ### 📂 Audit & Traceability

                    - Rule-level outcomes preserved  
                    - Confidence scores explain decisions  
                    - Escalation reasons clearly stated  
                    """
                )

            with gr.Tab("Documentation"):
                gr.Markdown(
                    """
                    ### 📖 Documentation

                    - JSON-only processing  
                    - Exportable reports  
                    - Extensible architecture  
                    """
                )

        # -------------------------------------------------
        # CONTROLS
        # -------------------------------------------------
        with gr.Row():
            run_btn = gr.Button("🚀 Run Compliance Validation")
            show_escalated = gr.Checkbox(
                label="Show only escalated invoices",
                value=False
            )

        # -------------------------------------------------
        # OUTPUTS
        # -------------------------------------------------
        summary_md = gr.Markdown(visible=False)
        escalation_note = gr.Markdown(visible=False)

        table_title = gr.Markdown(
            "### 📋 Actionable Compliance Report",
            visible=False
        )

        table_out = gr.Dataframe(
            headers=TABLE_COLUMN_LABELS,
            interactive=False,
            visible=False,
            wrap=True
        )

        llm_reasoning_out = gr.Markdown(
            visible=False,
            label="🧠 Compliance Summary using AI"
        )

        export_section = gr.Markdown(
            "### 📥 Export Report",
            visible=False
        )

        with gr.Row(visible=False) as export_row:
            csv_btn = gr.Button("Download CSV")
            pdf_btn = gr.Button("Download PDF")
            file_out = gr.File()

        # -------------------------------------------------
        # BUTTON HANDLER
        # -------------------------------------------------
        def handle_run(show_only_escalated):

            yield (
                gr.update(value="⏳ Processing invoices...", visible=True),
                gr.update(value="", visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
            )

            summary_text, df, esc_count, esc_msg, conflicts = run_pipeline(show_only_escalated)

            has_rows = len(df) > 0

            conflicts_md = (
                "### Compliance Summary using AI\n\n"
                + "\n".join(f"- {c}" for c in conflicts)
                if conflicts else ""
            )

            yield (
                gr.update(value=summary_text, visible=True),
                gr.update(value=esc_msg, visible=esc_count == 0),
                gr.update(value=df, visible=has_rows),
                gr.update(value=conflicts_md, visible=bool(conflicts_md)),
                gr.update(visible=has_rows),
                gr.update(visible=has_rows),
            )

        # -------------------------------------------------
        # WIRING
        # -------------------------------------------------
        run_btn.click(
            fn=handle_run,
            inputs=[show_escalated],
            outputs=[
                summary_md,
                escalation_note,
                table_out,
                llm_reasoning_out,
                export_section,
                export_row
            ]
        )

        csv_btn.click(fn=generate_csv, inputs=table_out, outputs=file_out)
        pdf_btn.click(fn=generate_pdf, inputs=table_out, outputs=file_out)

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------
        gr.HTML(
            """
            <hr>
            <div style="text-align:center;font-size:13px;color:#6b7280;">
                © Agentic AI Compliance Validator |
                <a href="https:www.linkedin.com/in/pravin-waghe-40646779" target="_blank">LinkedIn</a> |
                <a href="https://github.com/pravinraj2009-pixel/Compliance_Validator_Challenge"
                   target="_blank">GitHub</a>
            </div>
            """
        )

    # -------------------------------------------------
    # LAUNCH
    # -------------------------------------------------
    app.launch(
        css="""
        .navbar {
            display:flex;
            justify-content:space-between;
            border-bottom:1px solid #e5e7eb;
            margin-bottom:12px;
        }
        .subtitle {
            font-size:14px;
            color:#6b7280;
        }
        .nav-links a {
            margin-left:16px;
            font-size:14px;
            color:#2563eb;
            text-decoration:none;
        }
        .gradio-dataframe table {
            border-collapse: collapse !important;
            width: 100% !important;
            border: 2px solid #9ca3af !important;
        }

        .gradio-dataframe thead th {
            border-bottom: 2px solid #9ca3af !important;
            border-right: 1px solid #d1d5db !important;
            background-color: #f3f4f6 !important;
            font-weight: 700 !important;
            padding: 10px !important;
        }

        .gradio-dataframe tbody tr {
            border-bottom: 1px solid #d1d5db !important; 
        }

        .gradio-dataframe tbody td {
            border-right: 1px solid #e5e7eb !important;
            border-bottom: 1px solid #e5e7eb !important;
            padding: 10px !important;
            white-space: pre-wrap !important;
            word-break: break-word !important;
            vertical-align: top !important;
            max-width: 300px;
        }

        .gradio-dataframe tbody tr:last-child td {
            border-bottom: 2px solid #9ca3af !important;
        }

        """,
        allowed_paths=[".", "./docs", "./text"]
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    launch_ui()
