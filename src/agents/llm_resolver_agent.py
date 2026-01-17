
import requests

class LLMResolverAgent:
    def __init__(self, config):
        self.url = config["ollama"]["base_url"]
        self.model = config["ollama"]["model"]
        self.timeout = config["ollama"]["timeout"]

    def explain(self, context, conflicts):
        prompt = f"""
You are a compliance reasoning assistant.
Explain both interpretations neutrally.
Do NOT make a decision.

Context:
{context}

Conflicts:
{conflicts}
"""

        r = requests.post(
            f"{self.url}/api/generate",
            json={"model": self.model, "prompt": prompt},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json().get("response", "")
