import json
import csv
from collections import defaultdict
from datetime import datetime


class ReporterAgent:
    """
    Reporter Agent
    --------------
    Converts validation + resolution outputs into
    actionable, human-readable compliance reports.
    """

    def __init__(self, config=None):
        self.confidence_threshold = (
            config.get("confidence_threshold") if config else 0.7
        )

    def generate(self, invoice_ctx, validation_payload, resolver_output):
        results = validation_payload["results"]

        failed = [r for r in results if r.status == "FAIL"]
        review = [r for r in results if r.status == "REVIEW"]

        # ---- Group by category ----
        category_summary = defaultdict(list)
        for r in failed + review:
            category_summary[r.category].append({
                "check_id": r.check_id,
                "reason": r.reason,
                "evidence": r.evidence
            })

        # ---- Actionable recommendations ----
        recommendations = self._recommend_actions(failed, review)

        report = {
            "invoice_id": invoice_ctx.get("invoice_id"),
            "vendor_gstin": invoice_ctx.get("vendor_gstin"),
            "invoice_date": invoice_ctx.get("invoice_date"),
            "invoice_value": invoice_ctx.get("invoice_value"),

            "decision": resolver_output["decision"],
            "final_confidence": resolver_output.get("final_confidence"),
            "escalation_required": resolver_output.get("escalation_required", False),
            "primary_reason": resolver_output.get("primary_reason"),

            "failed_checks": [r.check_id for r in failed],
            "review_flags": [r.check_id for r in review],

            "category_summary": dict(category_summary),
            "recommended_actions": recommendations,

            "llm_reasoning": resolver_output.get("llm_reasoning"),

            "processing_time_sec": invoice_ctx
                .get("metadata", {})
                .get("processing_time_sec"),

            "generated_at": datetime.utcnow().isoformat()
        }

        return report

    # ---------------------------
    # Export helpers
    # ---------------------------

    def export_json(self, report, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def export_csv(self, report, path):
        flat = {
            "invoice_id": report["invoice_id"],
            "decision": report["decision"],
            "final_confidence": report["final_confidence"],
            "escalation_required": report["escalation_required"],
            "failed_checks": ",".join(report["failed_checks"]),
            "review_flags": ",".join(report["review_flags"]),
            "primary_reason": report["primary_reason"],
        }

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=flat.keys())
            writer.writeheader()
            writer.writerow(flat)

    # ---------------------------
    # Internal helpers
    # ---------------------------

    def _recommend_actions(self, failed, review):
        actions = []

        for r in failed + review:
            if r.check_id.startswith("B"):
                actions.append("Review GST compliance and correct invoice details")
            elif r.check_id.startswith("D"):
                actions.append("Verify TDS applicability and deductions")
            elif r.check_id.startswith("A"):
                actions.append("Verify invoice authenticity and document integrity")
            elif r.check_id.startswith("E"):
                actions.append("Check internal policy or approval requirements")

        return list(set(actions))
