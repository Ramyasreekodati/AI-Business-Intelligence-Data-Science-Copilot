# import removed: langgraph not required
from typing import Dict, Any

class SupervisorAgent:
    """Top‑level orchestrator that decides which sub‑agents to invoke.
    It receives the initial dataset metadata and returns a plan dict like:
    {
        "steps": ["cleaning", "eda", "insight", "report"],
        "status": "planned"
    }
    """

    def __init__(self, agents_registry: Dict[str, Any]):
        self.agents = agents_registry

    def plan(self, dataset_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Very naive planning – in a real system this would be an LLM call.
        steps = []
        if not context.get("cleaned"):
            steps.append("cleaning")
        if not context.get("eda"):
            steps.append("eda")
        if not context.get("insight"):
            steps.append("insight")
        steps.append("report")
        return {"steps": steps, "status": "planned"}

    def execute(self, dataset_id: str, context: Dict[str, Any]):
        plan = self.plan(dataset_id, context)
        for step in plan["steps"]:
            agent = self.agents.get(step)
            if agent:
                context = agent.run(dataset_id, context)
        return context
