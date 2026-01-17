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


def run_compliance_pipeline(config=None):
    start_time = time.time()

    extractor = ExtractorAgent(config)
    validator = ValidatorAgent(config)
    resolver = ResolverAgent(config)
    reporter = ReporterAgent(config)

    reports = []
    approved = 0
    escalated = 0

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

            try:
                validation_results = validator.validate(invoice_ctx)

                validation_payload = {
                    "results": validation_results,
                    "final_confidence": _compute_final_confidence(validation_results),
                }

                resolution = resolver.resolve(invoice_ctx, validation_payload)

                report = reporter.generate(
                    invoice_ctx,
                    validation_results,
                    resolution,
                )

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
