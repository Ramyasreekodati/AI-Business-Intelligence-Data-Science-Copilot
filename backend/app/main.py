from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router
from ...src.engine.auth_middleware import auth_middleware

app = FastAPI(
    title="AI Business Intelligence & Data Science Copilot",
    description="Production‑grade AI‑driven BI platform",
    version="0.1.0",
)

# Register the authentication middleware using FastAPI's decorator style
@app.middleware("http")
async def auth_middleware_wrapper(request: Request, call_next):
    return await auth_middleware(request, call_next)

# CORS (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes under /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
