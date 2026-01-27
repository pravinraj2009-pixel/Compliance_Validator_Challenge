import time
<<<<<<< HEAD
from concurrent.futures import ThreadPoolExecutor, as_completed
=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6

from src.agents.extractor_agent import ExtractorAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.resolver_agent import ResolverAgent
from src.agents.reporter_agent import ReporterAgent


<<<<<<< HEAD
# --------------------------------------------------
# Helpers
# --------------------------------------------------

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
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


<<<<<<< HEAD
def _aggregate_ai_summary(all_llm_reasoning):
    """
    Build generalized, de-duplicated AI summary bullets
    across ALL invoices.
    """
    bullets = set()

    for reasoning in all_llm_reasoning:
        if not reasoning:
            continue

        for line in reasoning:
            line = line.strip().lower()

            if not line:
                continue

            if "missing" in line:
                bullets.add(
                    "Missing critical invoice fields can lead to compliance failure"
                )
            elif "incomplete" in line:
                bullets.add(
                    "Incomplete invoice data often results in REVIEW outcomes"
                )
            elif "ambigu" in line:
                bullets.add(
                    "Ambiguous invoice information can cause mixed compliance outcomes"
                )
            elif "conflict" in line:
                bullets.add(
                    "Conflicting compliance signals may require human review"
                )

    return sorted(bullets)


# --------------------------------------------------
# PARALLEL WORKER
# --------------------------------------------------

def _process_single_invoice(invoice_ctx, validator, resolver, reporter):
    start = time.perf_counter()

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

    report["processing_time_sec"] = round(
        time.perf_counter() - start, 2
    )

    return report, resolution.get("llm_reasoning")


# --------------------------------------------------
# PIPELINE (UI ENTRY POINT)
# --------------------------------------------------

def run_compliance_pipeline(config, force_run: bool = False):
=======
def run_compliance_pipeline(config, force_run: bool = False):
    """Function wrapper for UI compatibility - processes all invoice files."""
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    start_time = time.time()

    extractor = ExtractorAgent(config)
    validator = ValidatorAgent(config)
    resolver = ResolverAgent(config)
    reporter = ReporterAgent(config)

    reports = []
    approved = 0
    escalated = 0

<<<<<<< HEAD
    all_llm_reasoning = []

    seen_invoice_ids = set()
    invoice_files = extractor.load_invoices()
    invoices = []

    # ---- Extract all invoices first (still sequential, fast) ----
    for file_path in invoice_files:
        try:
            extracted = extractor.extract(file_path)
            for inv in _expand_invoices(extracted):
                invoice_id = inv.get("invoice_id", "MISSING_ID")
                if invoice_id not in seen_invoice_ids:
                    seen_invoice_ids.add(invoice_id)
                    invoices.append(inv)
        except Exception as file_error:
            print(f"[ERROR] File extraction failed: {file_path.name} -> {file_error}")

    # ---- PARALLEL INVOICE PROCESSING ----
    MAX_WORKERS = min(8, len(invoices))  # sweet spot for IO-bound APIs

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                _process_single_invoice,
                invoice_ctx,
                validator,
                resolver,
                reporter
            )
            for invoice_ctx in invoices
        ]

        for future in as_completed(futures):
            try:
                report, llm_reasoning = future.result()
                reports.append(report)

                if llm_reasoning:
                    all_llm_reasoning.append(llm_reasoning)
=======
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
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6

                if report["decision"] == "APPROVE":
                    approved += 1
                else:
                    escalated += 1

<<<<<<< HEAD
            except Exception as e:
                print(f"[ERROR] Invoice processing failed: {e}")
                escalated += 1

    # ---- GLOBAL AI SUMMARY ----
    ai_compliance_summary = _aggregate_ai_summary(all_llm_reasoning)

=======
            except Exception as invoice_error:
                print(f"[ERROR] Invoice failed: {invoice_id} -> {invoice_error}")
                reports.append(
                    reporter.system_error(invoice_id, str(invoice_error))
                )
                escalated += 1

>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    summary = {
        "total_invoices": len(reports),
        "approved": approved,
        "escalated": escalated,
        "processing_time_sec": round(time.time() - start_time, 2),
<<<<<<< HEAD
        "ai_compliance_summary": ai_compliance_summary,
=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    }

    return summary, reports


<<<<<<< HEAD
# --------------------------------------------------
# PIPELINE (PROGRAMMATIC ENTRY POINT)
# --------------------------------------------------

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
class CompliancePipeline:
    def __init__(self, config):
        self.extractor = ExtractorAgent(config)
        self.validator = ValidatorAgent(config)
        self.resolver = ResolverAgent(config)
<<<<<<< HEAD
        self.reporter = ReporterAgent(config)

    def process(self, invoice_path):
        start_time = time.time()

        reports = []
        approved = 0
        escalated = 0
        all_llm_reasoning = []
=======
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
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6

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

<<<<<<< HEAD
        MAX_WORKERS = min(8, len(invoices))

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(
                    _process_single_invoice,
                    invoice,
                    self.validator,
                    self.resolver,
                    self.reporter
                )
                for invoice in invoices
            ]

            for future in as_completed(futures):
                try:
                    report, llm_reasoning = future.result()
                    reports.append(report)

                    if llm_reasoning:
                        all_llm_reasoning.append(llm_reasoning)

                    if report["decision"] == "APPROVE":
                        approved += 1
                    else:
                        escalated += 1

                except Exception as e:
                    reports.append(
                        self.reporter.system_error(
                            "UNKNOWN", str(e)
                        )
                    )
                    escalated += 1

        ai_compliance_summary = _aggregate_ai_summary(all_llm_reasoning)
=======
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
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6

        summary = {
            "total_invoices": len(reports),
            "approved": approved,
            "escalated": escalated,
<<<<<<< HEAD
            "processing_time_sec": round(time.time() - start_time, 2),
            "ai_compliance_summary": ai_compliance_summary,
=======
            "processing_time_sec": round(
                time.time() - start_time, 2
            ),
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        }

        return summary, reports
