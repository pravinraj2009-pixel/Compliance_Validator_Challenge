from src.models.validation_result import ValidationResult
from src.validation_checks.category_b import CATEGORY_B_CHECKS
from src.validation_checks.category_d import CATEGORY_D_CHECKS
from src.tools.gst_portal_client import GSTPortalClient


class GSTTDSValidatorAgent:
    """
    GST & TDS Validator Agent
    -------------------------
    Executes:
<<<<<<< HEAD
    - Category B: GST Compliance (FAIL-FAST)
    - Category D: TDS Compliance (only if GST passes)
=======
    - Category B: GST Compliance
    - Category D: TDS Compliance

>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    """

    def __init__(self, config):
        self.config = config
        self.client = GSTPortalClient(
            base_url=config["gst_api_base_url"],
            api_key=config["gst_api_key"],
        )

    def validate(self, invoice_ctx):
        if not isinstance(invoice_ctx, dict):
            raise TypeError("GSTTDSValidatorAgent expects invoice_ctx dict")

        results = []
<<<<<<< HEAD

        # =====================================================
        # GST VALIDATION (FAIL-FAST)
        # =====================================================

=======
        # Note: Confidence is calculated by pipeline's _compute_final_confidence()
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        # ---------------- GSTIN Validation (B1, B2) ----------------
        seller_gstin = invoice_ctx.get("seller_gstin")

        if seller_gstin:
            try:
                status, data = self.client.validate_gstin(seller_gstin)
<<<<<<< HEAD

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                if status != 200 or not data.get("valid"):
                    results.append(
                        ValidationResult(
                            check_id="B2",
                            category="GST",
                            status="FAIL",
                            reason=data.get("message", "Invalid GSTIN"),
                            confidence_impact=0.25,
                            evidence=data,
                        )
                    )
<<<<<<< HEAD
                    return results  # 🚨 FAIL-FAST

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                elif data.get("status") in ("SUSPENDED", "CANCELLED"):
                    results.append(
                        ValidationResult(
                            check_id="B2",
                            category="GST",
                            status="FAIL",
                            reason=f"GSTIN {data.get('status')}",
                            confidence_impact=0.20,
                            evidence=data,
                        )
                    )
<<<<<<< HEAD
                    return results  # 🚨 FAIL-FAST

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_id="B2",
                        category="GST",
                        status="REVIEW",
                        reason=f"GSTIN validation error: {str(e)}",
                        confidence_impact=0.10,
                    )
                )
<<<<<<< HEAD
                # REVIEW → continue GST checks
=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6

        # ---------------- IRN Validation (B12, B14) ----------------
        irn = invoice_ctx.get("irn")
        if irn:
            try:
                status, data = self.client.validate_irn(irn)
<<<<<<< HEAD

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                if status != 200 or not data.get("valid"):
                    results.append(
                        ValidationResult(
                            check_id="B14",
                            category="GST",
                            status="FAIL",
                            reason="Invalid or cancelled IRN",
                            confidence_impact=0.15,
                            evidence=data,
                        )
                    )
<<<<<<< HEAD
                    return results  # 🚨 FAIL-FAST

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_id="B14",
                        category="GST",
                        status="REVIEW",
                        reason=f"IRN validation error: {str(e)}",
                        confidence_impact=0.10,
                    )
                )

        # ---------------- HSN Rate Validation (B4, B6) ----------------
        invoice_date = invoice_ctx.get("invoice_date")
        line_items = invoice_ctx.get("line_items", [])

        for item in line_items:
            hsn = item.get("hsn_code")
            applied_igst = item.get("igst_rate")

            if not hsn or not invoice_date:
                continue

            try:
                status, rate_data = self.client.get_hsn_rate(hsn, invoice_date)
                expected_igst = rate_data.get("rate", {}).get("igst")

                if status != 200 or expected_igst is None:
                    results.append(
                        ValidationResult(
                            check_id="B6",
                            category="GST",
                            status="REVIEW",
                            reason="HSN rate lookup failed",
                            confidence_impact=0.10,
                            evidence=rate_data,
                        )
                    )
<<<<<<< HEAD

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                elif applied_igst != expected_igst:
                    results.append(
                        ValidationResult(
                            check_id="B6",
                            category="GST",
                            status="FAIL",
                            reason="GST rate mismatch with HSN",
                            confidence_impact=0.10,
                            evidence=rate_data,
                        )
                    )
<<<<<<< HEAD
                    return results  # 🚨 FAIL-FAST

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_id="B6",
                        category="GST",
                        status="REVIEW",
                        reason=f"HSN validation error: {str(e)}",
                        confidence_impact=0.10,
                    )
                )

        # ---------------- E-Invoice Requirement (B12) ----------------
        try:
            invoice_value = invoice_ctx.get("invoice_value") or 0
            status, einv = self.client.check_einvoice_required(
                seller_gstin,
                invoice_date,
                invoice_value,
            )

            if status == 200 and einv.get("required") and not irn:
                results.append(
                    ValidationResult(
                        check_id="B12",
                        category="GST",
                        status="FAIL",
                        reason="E-invoice required but IRN missing",
                        confidence_impact=0.15,
                        evidence=einv,
                    )
                )
<<<<<<< HEAD
                return results  # 🚨 FAIL-FAST

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        except Exception as e:
            results.append(
                ValidationResult(
                    check_id="B12",
                    category="GST",
                    status="REVIEW",
                    reason=f"E-invoice API error: {str(e)}",
                    confidence_impact=0.10,
                )
            )

<<<<<<< HEAD
        # =====================================================
        # TDS VALIDATION (ONLY IF GST PASSED)
        # =====================================================
=======
        # ---------------- Section 206AB (D10) ----------------
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        pan = invoice_ctx.get("vendor_pan")
        if pan:
            try:
                status, data = self.client.verify_206ab(pan)
                if status == 200 and data.get("section_206ab_applicable"):
                    results.append(
                        ValidationResult(
                            check_id="D10",
                            category="TDS",
                            status="REVIEW",
                            reason="Higher TDS under section 206AB applicable",
                            confidence_impact=0.10,
                            evidence=data,
                        )
                    )
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_id="D10",
                        category="TDS",
                        status="REVIEW",
                        reason=f"TDS verification error: {str(e)}",
                        confidence_impact=0.10,
                    )
                )

        # ---------------- Rule-Based Category B & D ----------------
        for check in CATEGORY_B_CHECKS + CATEGORY_D_CHECKS:
            try:
                result = check.validate(invoice_ctx)
                if isinstance(result, ValidationResult):
                    results.append(result)
            except Exception as e:
                results.append(
                    ValidationResult(
                        check_id=check.check_id,
                        category=check.category,
                        status="REVIEW",
                        reason=f"Rule execution error: {str(e)}",
                        confidence_impact=0.10,
                    )
                )

<<<<<<< HEAD
=======
        # Note: Final confidence is calculated by pipeline's _compute_final_confidence()
        # based on FAIL/REVIEW status and confidence_impact values in results

>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        return results
