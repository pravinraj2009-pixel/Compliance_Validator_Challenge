import json
from src.mcp.server import MCPServer
from src.mcp.tools.ollama_tool import ollama_resolver_tool
from src.storage.decision_store import DecisionStore


class ResolverAgent:
    """
    Resolver Agent
    --------------
    Responsibilities:
    - Detect conflicts & ambiguity
    - Apply confidence threshold
    - Detect historical-decision traps
    - Optionally use LLM for explanation
    - Decide APPROVE / REVIEW
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

        # ---- MCP + LLM (optional) ----
        self.mcp = None
        if (
            config["agentic"]["use_mcp"]
            and config["agentic"]["use_llm_resolver"]
        ):
            self.mcp = MCPServer()
            self.mcp.register_tool(
                "ollama.reason",
                ollama_resolver_tool(config)
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

    def _detect_conflicts(self, results):
        """
        Simple, explainable conflict detection.
        Can evolve without breaking behavior.
        """
        conflicts = []

        failed = [r for r in results if r.status == "FAIL"]
        review = [r for r in results if r.status == "REVIEW"]

        if failed and review:
            conflicts.append(
                "Mixed FAIL and REVIEW outcomes across compliance categories"
            )

        gst_fail = any(r.check_id.startswith("B") for r in failed)
        tds_fail = any(r.check_id.startswith("D") for r in failed)

        if gst_fail and tds_fail:
            conflicts.append(
                "GST and TDS rules conflict or jointly violated"
            )

        return conflicts

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

        # ---- Base deterministic decision ----
        if confidence < self.confidence_threshold:
            decision = "REVIEW"
            primary_reason = "Low confidence score"
        elif failed or review_flags:
            decision = "REVIEW"
            primary_reason = "Compliance issues detected"
        else:
            decision = "APPROVE"
            primary_reason = "All critical checks passed"

        # ---- Optional LLM resolver (explanation only) ----
        llm_explanation = None
        if conflicts and self.mcp:
            llm_explanation = self.mcp.call_tool(
                "ollama.reason",
                {
                    "invoice_context": {
                        "invoice_id": invoice_id,
                        "vendor_gstin": invoice_ctx.get("vendor_gstin"),
                        "amount": invoice_ctx.get("total_amount"),
                    },
                    "conflicts": conflicts,
                }
            )

        # ---- Persist decision ----
        self.db.log_decision(
            invoice_id=invoice_id,
            decision=decision,
            confidence=confidence
        )

        return {
            "decision": decision,
            "final_confidence": round(confidence, 3),
            "failed_checks": [r.check_id for r in failed],
            "review_flags": [r.check_id for r in review_flags],
            "conflicts": conflicts,
            "llm_resolver": llm_explanation,
            "deviated_from_history": deviated_from_history,
            "primary_reason": primary_reason,
            "escalation_required": decision == "REVIEW"
        }
