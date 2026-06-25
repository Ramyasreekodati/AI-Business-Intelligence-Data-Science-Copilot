
# AI Business Intelligence & Data Science Copilot

This repository is the **flagship engineering portfolio** that demonstrates a production‑grade AI‑driven Business Intelligence platform.

## Repository Layout
```
project/
│
├─ backend/                # FastAPI service
│   └─ app/
│       ├─ main.py        # FastAPI entry point
│       └─ api.py         # Router definitions (upload, analysis, etc.)
│
├─ agents/                 # LangGraph agents (hierarchical design)
│   ├─ supervisor_agent.py
│   ├─ business_agent.py
│   ├─ data_agent.py
│   ├─ ml_agent.py
│   ├─ report_agent.py
│   ├─ quality_agent.py
│   └─ security_agent.py
│
├─ src/engine/             # Core engine utilities
│   ├─ agent_hierarchy.py # Definition of the hierarchical agent classes
│   └─ memory.py           # Persistent AI‑memory implementation (vector + RDBMS)
│
├─ plugins/                # Industry plug‑ins (Sales, Finance, …)
│   ├─ __init__.py
│   └─ sales_plugin.py     # Example plug‑in exposing domain‑specific prompts & helpers
│
├─ docs/                   # All documentation books (already added)
│
├─ tests/                  # Unit / integration tests (to be added)
│
├─ Dockerfile              # Container image for the whole platform
├─ docker-compose.yml      # Development compose (API, DB, Redis, MLflow, etc.)
└─ pyproject.toml          # Poetry / PDM configuration (dependencies, scripts)
```

## How to Get Started
```bash
# Clone the repo (this folder is already a clone in the workspace)
cd project
# Build and start services
docker compose up -d
# The FastAPI docs are available at http://localhost:8000/docs
```

The rest of the documentation lives in the `docs/` folder and provides the full product blueprint, architecture decisions, and implementation guide.
