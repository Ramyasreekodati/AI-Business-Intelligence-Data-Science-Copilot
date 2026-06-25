from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid, shutil, os
import jwt
from datetime import datetime, timedelta
router = APIRouter()
class LoginRequest(BaseModel):
    username: str

@router.post("/login")
async def login(request: LoginRequest):
    payload = {
        "sub": request.username,
        "role": "analyst",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, os.getenv("JWT_SECRET", "supersecret"), algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}



DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/upload")
async def upload_dataset(request: Request, file: UploadFile = File(...)):
    # Role check – only analysts can upload datasets
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    if user.get("role") != "analyst":
        raise HTTPException(status_code=403, detail="Insufficient permissions for upload")
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    dataset_id = str(uuid.uuid4())
    dest_path = os.path.join(DATA_DIR, f"{dataset_id}.csv")
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(content={"dataset_id": dataset_id, "filename": file.filename})

@router.post("/analyze/{dataset_id}")
async def analyze_dataset(request: Request, dataset_id: str, background_tasks: BackgroundTasks):
    # Role check – only analysts can run analysis
    user = getattr(request.state, "user", None)
    if not user or user.get("role") != "analyst":
        raise HTTPException(status_code=403, detail="Insufficient permissions for analysis")
    # Initialize agents and supervisor
    from ...agents.supervisor_agent import SupervisorAgent
    from ...agents.data_agent import DataAgent
    from ...agents.eda_agent import EDAGent
    from ...agents.business_agent import BusinessAgent

    agents_registry = {
        "cleaning": DataAgent(),
        "eda": EDAGent(),
        "insight": BusinessAgent(),
        "report": BusinessAgent(),
    }
    supervisor = SupervisorAgent(agents_registry)
    context = {}
    result = supervisor.execute(dataset_id, context)
    return JSONResponse(content={"result": result})

@router.get("/job/{job_id}")
async def get_job_status(request: Request, job_id: str):
    # Role check – only analysts can view job status
    user = getattr(request.state, "user", None)
    if not user or user.get("role") != "analyst":
        raise HTTPException(status_code=403, detail="Insufficient permissions for job status")
    # Placeholder response
    return JSONResponse(content={"job_id": job_id, "status": "completed", "report_url": f"/reports/{job_id}.pdf"})
