from typing import List
from src.models.validation_result import ValidationResult


class ReporterAgent:
    """
    Reporter Agent
    --------------
    Produces final, human-readable, auditable compliance reports.

    Guarantees:
    - One report row per invoice
    - Never crashes
    - Clear escalation logic
    - Deterministic primary reason
    """

    def __init__(self, config=None):
        """
        Config is accepted for pipeline consistency and future extensibility.
        Currently not required by ReporterAgent logic.
        """
        self.config = config

    def generate(
        self,
        invoice_ctx: dict,
        validation_results: List[ValidationResult],
        resolution: dict,
    ) -> dict:
        invoice_id = invoice_ctx.get("invoice_id", "UNKNOWN")

        # -------------------------------
        # Failed & Review checks
        # -------------------------------
        failed = [r for r in validation_results if r.status == "FAIL"]
        review = [r for r in validation_results if r.status == "REVIEW"]

        # -------------------------------
        # Primary reason derivation
        # -------------------------------
        if failed:
            primary_reason = failed[0].reason or failed[0].check_id
        elif review:
            primary_reason = review[0].reason or review[0].check_id
        else:
            primary_reason = "All compliance checks passed"

        # -------------------------------
        # Confidence handling
        # -------------------------------
        confidence = resolution.get("final_confidence")
        if confidence is None:
            confidence = resolution.get("confidence", 0.0)

        # -------------------------------
        # Final report row
        # -------------------------------
        return {
            "invoice_id": invoice_id,
            "decision": resolution.get("decision", "ESCALATE"),
            "confidence": round(float(confidence), 3),
            "primary_reason": primary_reason,
            "failed_checks": [r.check_id for r in failed],
            "review_flags": [r.check_id for r in review],
            "escalation_required": resolution.get(
                "escalation_required",
                resolution.get("decision") != "APPROVE",
            ),
            "llm_reasoning": resolution.get("llm_reasoning"),
        }

    # ----------------------------------------------------
    # SYSTEM-LEVEL FAILURE (never break pipeline)
    # ----------------------------------------------------
    def system_error(self, invoice_id: str, error_message: str) -> dict:
        return {
            "invoice_id": invoice_id,
            "decision": "ESCALATE",
            "confidence": 0.0,
            "primary_reason": error_message,
            "failed_checks": ["SYSTEM_ERROR"],
            "review_flags": [],
            "escalation_required": True,
            "llm_reasoning": None,
        }
