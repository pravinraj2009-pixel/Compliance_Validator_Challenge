import time

from src.agents.extractor_agent import ExtractorAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.gst_tds_validator_agent import GSTTDSValidatorAgent
from src.agents.resolver_agent import ResolverAgent
from src.agents.reporter_agent import ReporterAgent


def run_compliance_pipeline(config):
    extractor = ExtractorAgent(config)
    validator = ValidatorAgent(config)
    gst_tds_validator = GSTTDSValidatorAgent(config)
    resolver = ResolverAgent(config)
    reporter = ReporterAgent(config)

    invoices = extractor.load_invoices()
    reports = []
    start_time = time.time()

    for invoice_path in invoices:
        try:
            invoice_ctx = extractor.extract(invoice_path)

            base_validation = validator.validate(invoice_ctx)
            gst_tds_validation = gst_tds_validator.validate(invoice_ctx)

            combined_results = (
                base_validation["results"]
                + gst_tds_validation["results"]
            )

            combined_payload = {
                "results": combined_results,
                "final_confidence": min(
                    base_validation["final_confidence"],
                    gst_tds_validation["final_confidence"]
                ),
                "conflicts": (
                    base_validation["conflicts"]
                    + gst_tds_validation.get("conflicts", [])
                ),
            }

            resolution = resolver.resolve(invoice_ctx, combined_payload)
            report = reporter.generate(
                invoice_ctx,
                combined_payload,
                resolution
            )
            reports.append(report)

        except Exception as e:
            reports.append({
                "invoice_id": getattr(invoice_path, "name", "UNKNOWN"),
                "decision": "ESCALATE",
                "confidence": 0.0,
                "primary_reason": str(e),
                "escalation_required": True
            })

    summary = {
        "total_invoices": len(reports),
        "approved": sum(r["decision"] == "APPROVE" for r in reports),
        "escalated": sum(r["decision"] != "APPROVE" for r in reports),
        "processing_time_sec": round(time.time() - start_time, 2),
    }

    return summary, reports
