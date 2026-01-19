import time

from src.agents.extractor_agent import ExtractorAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.resolver_agent import ResolverAgent
from src.agents.reporter_agent import ReporterAgent


def _expand_invoices(extracted):
    if extracted is None:
        return []
    if isinstance(extracted, list):
        return extracted
    return [extracted]


def _compute_final_confidence(results):
    if not results:
        return 1.0

    fail = sum(1 for r in results if r.status == "FAIL")
    review = sum(1 for r in results if r.status == "REVIEW")
    total = len(results)

    return max(0.0, 1.0 - ((fail * 0.3 + review * 0.15) / total))


def run_compliance_pipeline(config, force_run: bool = False):
    """Function wrapper for UI compatibility - processes all invoice files."""
    start_time = time.time()

    extractor = ExtractorAgent(config)
    validator = ValidatorAgent(config)
    resolver = ResolverAgent(config)
    reporter = ReporterAgent(config)

    reports = []
    approved = 0
    escalated = 0

    # Deduplicate only within current run
    seen_invoice_ids = set()

    invoice_files = extractor.load_invoices()

    for file_path in invoice_files:
        try:
            extracted = extractor.extract(file_path)
        except Exception as file_error:
            print(f"[ERROR] File extraction failed: {file_path.name} -> {file_error}")
            continue

        invoices = _expand_invoices(extracted)

        for invoice_ctx in invoices:
            invoice_id = invoice_ctx.get("invoice_id", "MISSING_ID")

            # Deduplicate within this run only
            if invoice_id in seen_invoice_ids:
                continue
            seen_invoice_ids.add(invoice_id)

            try:
                validation_results = validator.validate(invoice_ctx)
                print("\n==============================")
                print(f"[PIPELINE] Processing Invoice: {invoice_id}")

                print("[PIPELINE] Validation Results:")
                for vr in validation_results:
                    print(
                        f"  - check={vr.check_id} | status={vr.status} | reason={vr.reason}"
                    )

                validation_payload = {
                    "results": validation_results,
                    "final_confidence": _compute_final_confidence(validation_results),
                }

                resolution = resolver.resolve(invoice_ctx, validation_payload)
                print("[PIPELINE] Resolution:")
                for k, v in resolution.items():
                    print(f"  {k}: {v}")

                report = reporter.generate(
                    invoice_ctx,
                    validation_results,
                    resolution,
                )

                print("[PIPELINE] Final Report:")
                for k, v in report.items():
                    print(f"  {k}: {v}")
                reports.append(report)

                if report["decision"] == "APPROVE":
                    approved += 1
                else:
                    escalated += 1

            except Exception as invoice_error:
                print(f"[ERROR] Invoice failed: {invoice_id} -> {invoice_error}")
                reports.append(
                    reporter.system_error(invoice_id, str(invoice_error))
                )
                escalated += 1

    summary = {
        "total_invoices": len(reports),
        "approved": approved,
        "escalated": escalated,
        "processing_time_sec": round(time.time() - start_time, 2),
    }

    return summary, reports


class CompliancePipeline:
    def __init__(self, config):
        self.extractor = ExtractorAgent(config)
        self.validator = ValidatorAgent(config)
        self.resolver = ResolverAgent(config)
        self.reporter = ReporterAgent()

    def process(self, invoice_path):
        start_time = time.time()
        reports = []

        approved = 0
        escalated = 0
        context = {
            "processed_invoices": [],
            "aggregate_tds": {},
            "duplicate_tracker": set(),
            "errors": []
        }

        try:
            extracted = self.extractor.extract(invoice_path)
            invoices = _expand_invoices(extracted)
        except Exception as e:
            return {
                "summary": {
                    "total_invoices": 0,
                    "approved": 0,
                    "escalated": 1,
                    "processing_time_sec": round(time.time() - start_time, 2),
                },
                "reports": [
                    self.reporter.system_error(
                        str(invoice_path), str(e)
                    )
                ],
            }

        for invoice in invoices:
            invoice_id = invoice.get("invoice_id", "UNKNOWN")

            try:
                print(f"[PIPELINE] Processing Invoice: {invoice_id}")

                validation_results = self.validator.validate(invoice)

                # Compute final confidence from validation results
                from src.orchestration.compliance_pipeline import _compute_final_confidence
                validation_payload = {
                    "results": validation_results,
                    "final_confidence": _compute_final_confidence(validation_results),
                }

                decision = self.resolver.resolve(invoice, validation_payload)

                report = self.reporter.generate(
                    invoice, validation_results, decision
                )

                reports.append(report)

                if report["decision"] == "APPROVE":
                    approved += 1
                else:
                    escalated += 1

                context["processed_invoices"].append(invoice_id)

            except Exception as invoice_error:
                print(
                    f"[ERROR] Invoice failed: {invoice_id} -> {invoice_error}"
                )

                context["errors"].append(
                    {"invoice_id": invoice_id, "error": str(invoice_error)}
                )

                reports.append(
                    self.reporter.system_error(
                        invoice_id, str(invoice_error)
                    )
                )
                escalated += 1

        summary = {
            "total_invoices": len(reports),
            "approved": approved,
            "escalated": escalated,
            "processing_time_sec": round(
                time.time() - start_time, 2
            ),
        }

        return summary, reports
