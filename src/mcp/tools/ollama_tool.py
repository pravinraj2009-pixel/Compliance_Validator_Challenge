
from src.agents.llm_resolver_agent import LLMResolverAgent

def ollama_resolver_tool(config):
    agent = LLMResolverAgent(config)

    def run(payload):
        context = payload.get("invoice_context") or payload.get("context", {})
        conflicts = payload.get("conflicts", [])
        return agent.explain(context, conflicts)

    return run
