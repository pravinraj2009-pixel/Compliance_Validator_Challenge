import pandas as pd
import gradio as gr

from src.orchestration.compliance_pipeline import run_compliance_pipeline
from src.config import load_config
from utils.download_csv import generate_csv
from utils.download_pdf import generate_pdf


def run_pipeline():
    """
    Executes the full agentic compliance pipeline.
    Returns:
      - Batch summary (JSON)
      - Full actionable report dataframe
    """
    config = load_config()
    summary, reports = run_compliance_pipeline(config)
    return summary, pd.DataFrame(reports)


def filter_escalated(df, show_only):
    if show_only:
        return df[df["escalation_required"] == True]
    return df


def launch_ui():
    with gr.Blocks(title="Agentic AI Compliance Validator") as app:

        # ------------------------------
        # Header
        # ------------------------------
        gr.Markdown(
            """
            # 🧠 Agentic AI Compliance Validator

            **Multi-Agent Pipeline**
            1️⃣ Extractor Agent – parses invoices (PDF / Image / CSV / JSON)  
            2️⃣ Validator Agents – 58-point GST / TDS / Policy checks  
            3️⃣ Resolver Agent – handles ambiguity & conflicts (LLM-assisted)  
            4️⃣ Reporter Agent – generates actionable compliance reports  

            *Built for explainability, auditability, and human-in-the-loop review.*
            """
        )

        # ------------------------------
        # Controls
        # ------------------------------
        run_btn = gr.Button("🚀 Run Compliance Validation")
        show_escalated = gr.Checkbox(
            label="Show only escalated invoices",
            value=False
        )

        # ------------------------------
        # Outputs
        # ------------------------------
        summary_out = gr.JSON(label="📊 Batch Summary & Agent Timings")
        table_out = gr.Dataframe(
            label="📋 Actionable Compliance Report",
            interactive=False
        )

        llm_reasoning_out = gr.JSON(
            label="🧠 LLM Reasoning (Resolver – Sample Escalation)",
            visible=True
        )

        state_df = gr.State()

        # ------------------------------
        # Pipeline Execution
        # ------------------------------
        run_btn.click(
            fn=run_pipeline,
            outputs=[summary_out, state_df]
        ).then(
            fn=lambda df, flag: filter_escalated(df, flag),
            inputs=[state_df, show_escalated],
            outputs=table_out
        ).then(
            fn=lambda df: (
                df[df["llm_reasoning"].notnull()]
                .iloc[0]["llm_reasoning"]
                if "llm_reasoning" in df.columns and df["llm_reasoning"].notnull().any()
                else {"info": "No LLM reasoning required for this batch"}
            ),
            inputs=state_df,
            outputs=llm_reasoning_out
        )

        # ------------------------------
        # Downloads
        # ------------------------------
        gr.Markdown("### 📥 Export Reports")

        csv_btn = gr.Button("Download CSV")
        pdf_btn = gr.Button("Download PDF")
        file_out = gr.File()

        csv_btn.click(fn=generate_csv, inputs=state_df, outputs=file_out)
        pdf_btn.click(fn=generate_pdf, inputs=state_df, outputs=file_out)

    app.launch()


if __name__ == "__main__":
    launch_ui()
