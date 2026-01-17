
class ValidationResult:
    def __init__(self, check_id, category, status, reason=None, confidence_impact=0.0, evidence=None, metadata=None):
        self.check_id = check_id
        self.category = category
        self.status = status
        self.reason = reason
        self.confidence_impact = confidence_impact
        self.evidence = evidence or {}
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "check_id": self.check_id,
            "category": self.category,
            "status": self.status,
            "reason": self.reason,
            "confidence_impact": self.confidence_impact,
            "evidence": self.evidence,
            "metadata": self.metadata,
        }
