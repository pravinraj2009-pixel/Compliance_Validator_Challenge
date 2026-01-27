import json
from src.mcp.server import MCPServer
<<<<<<< HEAD
from src.mcp.tools.groq_api_tool import groq_resolver_tool
from src.storage.decision_store import DecisionStore


def normalize_llm_explanation(text):
    """
    Normalize LLM free-form explanation into a list of
    clean, UI-safe bullet points.
    """
    if not text:
        return []

    lines = text.split("\n")
    normalized = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = line.lstrip("-•0123456789. ").strip()

        # Drop generic intro fluff
        if line.lower().startswith("based on"):
            continue

        normalized.append(line)

    return normalized


=======
from src.mcp.tools.ollama_tool import ollama_resolver_tool
from src.storage.decision_store import DecisionStore


>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
class ResolverAgent:
    """
    Resolver Agent
    --------------
    Responsibilities:
    - Detect conflicts & ambiguity
    - Apply confidence threshold
    - Detect historical-decision traps
    - Use LLM for summarization
    - Decide APPROVE / APPROVE_WITH_REVIEW / ESCALATE
    - Persist final decision (SQLite)
    """

    def __init__(self, config):
        self.config = config
        self.confidence_threshold = config["confidence_threshold"]

        # ---- Historical decisions (JSONL) ----
        self.history_path = config["historical_decisions_path"]
        self.history = self._load_history()

        # ---- SQLite audit store ----
        self.db = DecisionStore(config["sqlite"]["db_path"])

<<<<<<< HEAD
        # ---- MCP + LLM ----
=======
        # ---- MCP + LLM Call ----
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        self.mcp = None
        if (
            config["agentic"]["use_mcp"]
            and config["agentic"]["use_llm_resolver"]
        ):
            self.mcp = MCPServer()
            self.mcp.register_tool(
<<<<<<< HEAD
                "groq.reason",
                groq_resolver_tool(config)
=======
                "ollama.reason",
                ollama_resolver_tool(config)
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
            )

    def _load_history(self):
        history = []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                for line in f:
                    history.append(json.loads(line))
        except FileNotFoundError:
            pass
        return history

<<<<<<< HEAD
    # =====================================================
    # CONFLICT DETECTION (RULE-BASED)
    # =====================================================
=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    def _detect_conflicts(self, results):
        conflicts = []

        failed = [r for r in results if r.status == "FAIL"]
        review = [r for r in results if r.status == "REVIEW"]

        if failed and review:
            conflicts.append(
                "Mixed FAIL and REVIEW outcomes across compliance categories"
            )

        gst_fail = any(r.category == "GST" for r in failed)
        tds_fail = any(r.category == "TDS" for r in failed)

        if gst_fail and tds_fail:
            conflicts.append(
                "GST and TDS rules conflict or jointly violated"
            )

<<<<<<< HEAD
        # ✅ NEW: Explicit conflict when GST FAIL occurs
        if gst_fail and not conflicts:
            conflicts.append(
                "Critical GST compliance failure detected requiring escalation"
            )

        return conflicts

    # =====================================================
    # RESOLUTION
    # =====================================================
=======
        return conflicts

>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
    def resolve(self, invoice_ctx, validation_payload):
        results = validation_payload["results"]
        confidence = validation_payload["final_confidence"]

        failed = [r for r in results if r.status == "FAIL"]
        review_flags = [r for r in results if r.status == "REVIEW"]

        # ---- Conflict detection ----
        conflicts = self._detect_conflicts(results)

        # ---- Historical Trap Detection ----
        deviated_from_history = False
        invoice_id = invoice_ctx.get("invoice_id")

        for record in self.history:
            if record.get("invoice_id") == invoice_id:
                if record.get("decision") == "APPROVE" and failed:
                    deviated_from_history = True

<<<<<<< HEAD
        # ---- Determine blocking REVIEWs ----
=======
        # ---- Determine blocking REVIEWs (domain-specific) ----
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        blocking_review = any(
            r.category == "GST" for r in review_flags
        )

        # =====================================================
<<<<<<< HEAD
        # FINAL DECISION LOGIC
=======
        # ---- FINAL DECISION LOGIC
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        # =====================================================
        if failed:
            decision = "ESCALATE"
            primary_reason = "One or more critical compliance checks failed"

        elif confidence < self.confidence_threshold:
            decision = "APPROVE_WITH_REVIEW"
            primary_reason = "Confidence below approval threshold"

        elif blocking_review:
            decision = "APPROVE_WITH_REVIEW"
            primary_reason = "GST compliance requires human review"

        elif deviated_from_history:
            decision = "APPROVE_WITH_REVIEW"
            primary_reason = "Deviation from historical approval pattern"

        else:
            decision = "APPROVE"
            primary_reason = "All critical compliance checks passed"

<<<<<<< HEAD
        # =====================================================
        # LLM RESOLVER (AI SUMMARY)
        # =====================================================
        llm_explanation = None

        # ✅ Allow LLM on ESCALATE even if conflicts are minimal
        if (conflicts or decision == "ESCALATE") and self.mcp:
            try:
                raw_llm_output = self.mcp.call_tool(
                    "groq.reason",
=======
        # ---- LLM resolver 
        llm_explanation = None
        if conflicts and self.mcp:
            try:
                llm_explanation = self.mcp.call_tool(
                    "ollama.reason",
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
                    {
                        "invoice_context": {
                            "invoice_id": invoice_id,
                            "vendor_gstin": invoice_ctx.get("vendor_gstin"),
                            "amount": invoice_ctx.get("total_amount"),
                        },
                        "conflicts": conflicts,
                    }
                )
<<<<<<< HEAD

                llm_explanation = normalize_llm_explanation(raw_llm_output)

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
            except Exception as llm_error:
                print(f"[WARNING] LLM resolver failed: {llm_error}")
                llm_explanation = None

<<<<<<< HEAD
        # =====================================================
        # UI SAFETY FIXES
        # =====================================================

        # ✅ If escalated and no review flags (fail-fast case)
        if decision == "ESCALATE" and not review_flags:
            review_flags = [
                type(
                    "SyntheticReview",
                    (),
                    {"check_id": "Critical GST failure — manual review required"}
                )()
            ]

=======
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        # ---- Persist decision ----
        self.db.log_decision(
            invoice_id=invoice_id,
            decision=decision,
            confidence=confidence
        )
<<<<<<< HEAD

        # ---- DEBUG ----
=======
        # ---- DEBUG DECISION SUMMARY ----
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        print(
            f"[DECISION DEBUG] Invoice={invoice_id} | "
            f"Decision={decision} | "
            f"Confidence={confidence} | "
            f"Failed={len(failed)} | "
            f"Review={len(review_flags)} | "
            f"Conflicts={len(conflicts)}"
        )
<<<<<<< HEAD

        # =====================================================
        # FINAL PAYLOAD
        # =====================================================
=======
        # ---- FINAL PAYLOAD ----
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
        return {
            "decision": decision,
            "final_confidence": round(confidence, 3),
            "failed_checks": [r.check_id for r in failed],
            "review_flags": [r.check_id for r in review_flags],
<<<<<<< HEAD
            "conflicts": conflicts,                 # rule-based (table)
            "llm_reasoning": llm_explanation,        # AI summary
            "deviated_from_history": deviated_from_history,
            "primary_reason": primary_reason,
            "escalation_required": decision == "ESCALATE",
        }
=======
            "conflicts": conflicts,
            "llm_resolver": llm_explanation,
            "deviated_from_history": deviated_from_history,
            "primary_reason": primary_reason,
            "escalation_required": decision == "ESCALATE",
        }
>>>>>>> 507c4561faf35b246d6d8207ac15a538e2aa91a6
