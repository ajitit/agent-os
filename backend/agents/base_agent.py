"""
File: base_agent.py

Purpose:
Provides the foundational BaseAgent class that all specific AI agents inherit from,
defining common properties and access to the agent runtime.

Key Functionalities:
- Initialize base properties for agents (name, model)
- Provide access to the AgentRuntime instance for the agent

Inputs:
- Agent name
- LLM model identifier (default: "gpt-4")

Outputs:
- Configured BaseAgent instances
- AgentRuntime instances

Interacting Files / Modules:
- backend.kernel.runtime
"""
from backend.kernel.runtime import AgentRuntime

class BaseAgent:

    def __init__(self, name, model="gpt-4"):
        self.name = name
        self.model = model

    def runtime(self):
        return AgentRuntime(self)
