from backend.kernel.runtime import AgentRuntime

class BaseAgent:

    def __init__(self, name, model="gpt-4"):
        self.name = name
        self.model = model

    def runtime(self):
        return AgentRuntime(self)
