class BusinessAgent:
    """Handles business‑logic orchestration (e.g., KPI selection, recommendation policies)."""

    def __init__(self, config=None):
        self.config = config or {}

    def run(self, dataset_id: str, context: dict) -> dict:
        # Placeholder: add a dummy KPI list to the context
        context.setdefault("kpis", ["revenue", "profit", "customer_churn"])
        context["business"] = {"status": "processed"}
        return context
