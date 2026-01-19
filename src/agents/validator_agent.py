from src.models.validation_result import ValidationResult
from src.agents.gst_tds_validator_agent import GSTTDSValidatorAgent


class ValidatorAgent:
    """
    Validator Agent
    ----------------
    Runs all validators and guarantees that the output is a list of
    ValidationResult objects.
    """

    def __init__(self, config=None):
        if config is None:
            raise ValueError("config is required for ValidatorAgent")
        
        self.config = config
        self.validators = config.get("validators", [])
        self.gst_tds_agent = GSTTDSValidatorAgent(config)

    def validate(self, invoice_ctx: dict):
        results = []

        # ------------------------------------------------
        # GST / TDS Agent 
        # ------------------------------------------------
        try:
            gst_tds_results = self.gst_tds_agent.validate(invoice_ctx)

            if gst_tds_results:
                for item in gst_tds_results:
                    if isinstance(item, ValidationResult):
                        results.append(item)

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
            results.append(
                ValidationResult(
                    check_id="GSTTDSValidatorAgent",
                    category="GST_TDS",
                    status="REVIEW",
                    reason=f"GST/TDS agent error: {str(e)}"
                )
            )

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
