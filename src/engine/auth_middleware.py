from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

# Simple JWT verification – expects a HS256 token with secret in env var JWT_SECRET
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

auth_scheme = HTTPBearer(auto_error=False)  # Do not auto-raise; handle missing token manually

def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def auth_middleware(request: Request, call_next):
    # Skip auth for open endpoints (health, docs, upload) – you can customize this list
    open_paths = ["/healthz", "/docs", "/openapi.json", "/api/v1/login"]
    if any(request.url.path.startswith(p) for p in open_paths):
        response = await call_next(request)
        return response

    # Expect Authorization: Bearer <token>
    # Retrieve credentials; if missing, return 401 response
    credentials: HTTPAuthorizationCredentials = await auth_scheme(request)
    if credentials is None:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})
    try:
        payload = verify_token(credentials)
    except HTTPException as exc:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    # Attach user info to request.state for downstream use
    request.state.user = payload
    response = await call_next(request)
    return response
