import pandas as pd
import gradio as gr

from src.orchestration.compliance_pipeline import run_compliance_pipeline
from src.config import load_config
from utils.download_csv import generate_csv
from utils.download_pdf import generate_pdf


TABLE_COLUMNS = [
    "invoice_id",
    "decision",
    "final_confidence",
    "primary_reason",
    "escalation_required",
    "failed_checks",
    "review_flags",
    "conflicts",
    "deviated_from_history",
]


def run_pipeline(show_only_escalated: bool):
    config = load_config()
    summary, reports = run_compliance_pipeline(config)

    rows = []
    escalation_count = 0
    llm_reasoning = None

    for r in reports:
        is_escalated = bool(r.get("escalation_required"))
        if is_escalated:
            escalation_count += 1

        rows.append({
            "invoice_id": r.get("invoice_id", ""),
            "decision": r.get("decision", ""),
            "final_confidence": r.get("final_confidence", ""),
            "primary_reason": r.get("primary_reason", ""),
            "escalation_required": "Yes" if is_escalated else "No",
            "failed_checks": ", ".join(r.get("failed_checks", [])),
            "review_flags": ", ".join(r.get("review_flags", [])),
            "conflicts": ", ".join(r.get("conflicts", [])),
            "deviated_from_history": r.get("deviated_from_history", False),
        })

        if llm_reasoning is None and r.get("llm_resolver"):
            llm_reasoning = r["llm_resolver"]

    df = pd.DataFrame(rows, columns=TABLE_COLUMNS)

    if show_only_escalated:
        df = df[df["escalation_required"] == "Yes"]

    approved = len(df) - escalation_count

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

    if not isinstance(llm_reasoning, dict):
        llm_reasoning = {
            "Information": "No information is available for these invoices."
        }

    return (
        summary_text,
        df,
        escalation_count,
        escalation_msg,
        llm_reasoning
    )


def launch_ui():
    with gr.Blocks(title="Agentic AI Compliance Validator") as app:

        # -------- Header --------
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
                    <a href="./file=text/Compliance Validator System Architecture Document.docx" target="_blank">Architecture</a>
                    <a href="./file=docs/Compliance Validator System_Dry_Run_Walkthrough.docx" target="_blank">Walkthrough</a>
                    <a href="./file=README.md" target="_blank">README</a>
                </div>
            </div>
            """
        )

        # -------- Tabs (RESTORED) --------
        # -------------------------------------------------
        # Tabs (Pages)
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

                    Designed for **accuracy, trust, and scalability**.
                    """
                )

            with gr.Tab("Agent Architecture"):
                gr.Markdown(
                    """
                    ### 🧠 Agent Architecture

                    **Extractor Agent**  
                    Normalizes incoming invoice data (JSON for this assessment)

                    **Validator Agents**  
                    Perform rule-based GST, TDS, and policy checks

                    **Resolver Agent**  
                    Handles ambiguity and conflicts  
                    Uses LLMs only for explanation (not decision-making)

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
                    - Historical decision comparison supported
                    """
                )

            with gr.Tab("Documentation"):
                gr.Markdown(
                    """
                    ### 📖 Documentation & Extensibility

                    - JSON-only implementation (per requirements)  
                    - Designed for PDF/Image extensibility  
                    - Mock APIs and LLM tools are pluggable  
                    """
                )

        # -------- Controls --------
        with gr.Row():
            run_btn = gr.Button("🚀 Run Compliance Validation")
            show_escalated = gr.Checkbox(
                label="Show only escalated invoices",
                value=False
            )

        # -------- Outputs (hidden initially) --------
        summary_md = gr.Markdown(visible=False)
        escalation_note = gr.Markdown(visible=False)

        table_out = gr.Dataframe(
            headers=TABLE_COLUMNS,
            interactive=False,
            visible=False,
            label="📋 Actionable Compliance Report"
        )

        llm_reasoning_out = gr.JSON(
            visible=False,
            label="🧠 Escalation Reasons"
        )

        export_section = gr.Markdown(
            "### 📥 Export Report",
            visible=False
        )

        with gr.Row(visible=False) as export_row:
            csv_btn = gr.Button("Download CSV")
            pdf_btn = gr.Button("Download PDF")
            file_out = gr.File()

        # -------- Button Logic --------
        def handle_run(show_only_escalated):
            summary_text, df, esc_count, esc_msg, llm = run_pipeline(show_only_escalated)

            return (
                gr.update(value=summary_text, visible=True),
                gr.update(value=esc_msg, visible=esc_count == 0),
                gr.update(value=df, visible=esc_count > 0),
                gr.update(value=llm, visible=esc_count > 0),
                gr.update(visible=esc_count > 0),
                gr.update(visible=esc_count > 0)
            )

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

        # -------- Footer --------
        gr.HTML(
            """
            <hr>
            <div style="text-align:center;font-size:13px;color:#6b7280;">
                © Agentic AI Compliance Validator |
                <a href="https://www.linkedin.com" target="_blank">LinkedIn</a> |
                <a href="https://github.com/pravinraj2009-pixel/Compliance_Validator_Challenge"
                   target="_blank">GitHub</a>
            </div>
            """
        )

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
        """,
        allowed_paths=[".", "./docs", "./text"]
    )


if __name__ == "__main__":
    launch_ui()
