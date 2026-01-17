from src.validation_checks.category_a import CATEGORY_A_CHECKS
from src.validation_checks.category_c import CATEGORY_C_CHECKS
from src.storage.invoice_store import InvoiceStore
from src.models.validation_result import ValidationResult


class ValidatorAgent:
    """
    Validator Agent
    ----------------
    Executes:
    - Category A (Document Authenticity)
    - Category C (Arithmetic & Calculation)

    Produces:
    - Validation results
    - Confidence score
    - Conflict signals (for Resolver)
    """

    def __init__(self, config):
        self.confidence_threshold = config["confidence_threshold"]
        self.store = InvoiceStore(config["sqlite"]["db_path"])

    def validate(self, invoice_ctx):
        results = []
        conflicts = []
        confidence = 1.0

        invoice_id = invoice_ctx.get("invoice_id", "UNKNOWN")

        # ---------- Stateful Duplicate Check (A2) ----------
        if self.store.is_duplicate(invoice_id):
            results.append(
                ValidationResult(
                    check_id="A2",
                    category="Document Authenticity",
                    status="FAIL",
                    reason="Duplicate invoice detected across batch",
                    confidence_impact=0.15
                )
            )
            confidence -= 0.15
        else:
            self.store.record(invoice_id)

        # ---------- Category A ----------
        for check in CATEGORY_A_CHECKS:
            if check.check_id == "A2":
                continue

            result = check.validate(invoice_ctx)

            # Missing data → REVIEW, not FAIL
            if result.status == "FAIL" and result.reason == "Missing data":
                result.status = "REVIEW"
                result.confidence_impact = 0.05

            results.append(result)
            confidence -= result.confidence_impact

        # ---------- Category C ----------
        for check in CATEGORY_C_CHECKS:
            result = check.validate(invoice_ctx)

            if result.status == "FAIL" and result.reason == "Missing data":
                result.status = "REVIEW"
                result.confidence_impact = 0.05

            results.append(result)
            confidence -= result.confidence_impact

        # ---------- Conflict Detection (Example) ----------
        if invoice_ctx.get("total_amount", 0) == 0:
            conflicts.append({
                "type": "INSUFFICIENT_DATA",
                "details": "Invoice total amount missing or zero"
            })

        confidence = round(max(confidence, 0.0), 3)

        return {
            "results": results,
            "final_confidence": confidence,
            "conflicts": conflicts
        }
