from src.models.validation_result import ValidationResult


class ValidatorAgent:
    """
    Validator Agent
    ----------------
    Runs all validators and guarantees that the output is a list of
    ValidationResult objects.

    HARD CONTRACT:
    validate(...) -> List[ValidationResult]
    """

    def __init__(self, config=None):
        self.config = config
        self.validators = config.get("validators", []) if config else []

    def validate(self, invoice_ctx: dict):
        results = []

        for validator in self.validators:
            try:
                output = validator.validate(invoice_ctx)

                if not output:
                    continue

                for item in output:
                    if isinstance(item, ValidationResult):
                        results.append(item)

                    elif isinstance(item, str):
                        # 🔒 Normalize string errors into REVIEW results
                        results.append(
                            ValidationResult(
                                check_id=validator.__class__.__name__,
                                status="REVIEW",
                                reason=item
                            )
                        )

                    else:
                        # 🔒 Catch-all for unexpected return types
                        results.append(
                            ValidationResult(
                                check_id=validator.__class__.__name__,
                                status="REVIEW",
                                reason=f"Unexpected validator output: {type(item)}"
                            )
                        )

            except Exception as e:
                # 🔒 Absolute isolation: validator can never kill invoice
                results.append(
                    ValidationResult(
                        check_id=validator.__class__.__name__,
                        status="REVIEW",
                        reason=f"Validator exception: {str(e)}"
                    )
                )

        return results
