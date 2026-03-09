class AgentRuntime:

    def __init__(self, agent):
        self.agent = agent

    async def execute(self, task):
        context = await self.observe(task)
        plan = await self.plan(context)
        result = await self.act(plan)
        await self.reflect(result)
        return result

    async def observe(self, task):
        return {"goal": task}

    async def plan(self, context):
        return {"steps":["analyze","execute"]}

    async def act(self, plan):
        return {"result":"completed"}

    async def reflect(self, result):
        pass
