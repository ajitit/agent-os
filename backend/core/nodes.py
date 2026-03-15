"""
File: nodes.py

Purpose:
Defines LangGraph node functions that wrap Vishwakarma agents, allowing them to be
used within a StateGraph.

Key Functionalities:
- `create_agent_node`: Factory function to create a node for a specific agent.
- Integration with Vishwakarma `BaseAgent` and `BaseLLMAdapter`.
"""

from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage

from backend.api.stores import agent_get
from backend.core.engine import AgentState


def create_agent_node(agent_id: str) -> Callable:
    """
    Creates a LangGraph node function for a given Vishwakarma agent.
    """
    async def agent_node(state: AgentState) -> dict[str, Any]:
        agent = agent_get(agent_id)
        if not agent:
            return {"messages": [AIMessage(content=f"Error: Agent {agent_id} not found.")]}

        # Get the last human message
        last_message = state["messages"][-1].content

        # Mocking the agent execution for now
        # In a real implementation, we would call agent.run(last_message)
        # which would use the LLM adapter and any tools.
        response = f"[Agent: {agent['name']}] Processing request: {last_message}"

        return {
            "messages": [AIMessage(content=response)],
            "results": {agent_id: "success"}
        }

    return agent_node
