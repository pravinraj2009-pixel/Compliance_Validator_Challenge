from src.models.validation_result import ValidationResult
from src.agents.gst_tds_validator_agent import GSTTDSValidatorAgent


class ValidatorAgent:
    """
    Validator Agent
    ----------------
    Runs all validators and guarantees that the output is a list of
    ValidationResult objects.
<<<<<<< HEAD

    FAIL-FAST BEHAVIOR:
    - If any GST validation FAIL occurs, stop all remaining validators
=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    """

    def __init__(self, config=None):
        if config is None:
            raise ValueError("config is required for ValidatorAgent")
<<<<<<< HEAD

=======
        
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        self.config = config
        self.validators = config.get("validators", [])
        self.gst_tds_agent = GSTTDSValidatorAgent(config)

    def validate(self, invoice_ctx: dict):
        results = []

<<<<<<< HEAD
        # =================================================
        # GST / TDS Agent (FAIL-FAST)
        # =================================================
=======
        # ------------------------------------------------
        # GST / TDS Agent 
        # ------------------------------------------------
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        try:
            gst_tds_results = self.gst_tds_agent.validate(invoice_ctx)

            if gst_tds_results:
                for item in gst_tds_results:
<<<<<<< HEAD

                    if isinstance(item, ValidationResult):
                        results.append(item)

                        # 🚨 FAIL-FAST: stop everything on GST FAIL
                        if item.category == "GST" and item.status == "FAIL":
                            return results

=======
                    if isinstance(item, ValidationResult):
                        results.append(item)

>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                    elif isinstance(item, str):
                        results.append(
                            ValidationResult(
                                check_id="GSTTDSValidatorAgent",
                                category="GST_TDS",
                                status="REVIEW",
                                reason=item
                            )
                        )

                    else:
                        results.append(
                            ValidationResult(
                                check_id="GSTTDSValidatorAgent",
                                category="GST_TDS",
                                status="REVIEW",
                                reason=f"Unexpected GST/TDS output: {type(item)}"
                            )
                        )

        except Exception as e:
<<<<<<< HEAD
            # If GST/TDS agent itself errors, treat as REVIEW and stop
            return [
=======
            results.append(
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                ValidationResult(
                    check_id="GSTTDSValidatorAgent",
                    category="GST_TDS",
                    status="REVIEW",
                    reason=f"GST/TDS agent error: {str(e)}"
                )
<<<<<<< HEAD
            ]

        # =================================================
        # OTHER VALIDATORS (ONLY IF GST PASSED)
        # =================================================
=======
            )

>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        for validator in self.validators:
            try:
                output = validator.validate(invoice_ctx)

                if not output:
                    continue

                for item in output:
                    if isinstance(item, ValidationResult):
                        results.append(item)

                    elif isinstance(item, str):
                        results.append(
                            ValidationResult(
                                check_id=validator.__class__.__name__,
                                category="VALIDATION",
                                status="REVIEW",
                                reason=item
                            )
                        )

                    else:
                        results.append(
                            ValidationResult(
                                check_id=validator.__class__.__name__,
                                category="VALIDATION",
                                status="REVIEW",
                                reason=f"Unexpected validator output: {type(item)}"
                            )
                        )

            except Exception as e:
                results.append(
                    ValidationResult(
                        check_id=validator.__class__.__name__,
                        category="VALIDATION",
                        status="REVIEW",
                        reason=f"Validator exception: {str(e)}"
                    )
                )

        return results
