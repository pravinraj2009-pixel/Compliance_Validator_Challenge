
from src.agents.llm_resolver_agent import LLMResolverAgent

def ollama_resolver_tool(config):
    agent = LLMResolverAgent(config)

    def run(payload):
        return agent.explain(payload["context"], payload["conflicts"])

    return run
