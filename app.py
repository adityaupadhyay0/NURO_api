from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends, status, Request
from pydantic import BaseModel
import shutil
import os
import uuid
import json
from werkzeug.utils import secure_filename
import logging
from datetime import datetime, timedelta, UTC
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.neuro_engine import NeuroEngine
from services.brain_orchestrator import CampaignBrain
from core.database import SessionLocal, AnalysisTask, Campaign, MarketingResult, User
from core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_db,
    require_admin,
    require_marketer,
    require_viewer,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="NeuroMark Pro 10x API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from core.config import UPLOAD_DIR, RESULTS_DIR

# Global instances
engine = None
brain = CampaignBrain()

class AnalysisResponse(BaseModel):
    task_id: str
    status: str

class MarketingResultIn(BaseModel):
    task_id: str
    ctr: float
    cpc: float = None
    cpa: float = None
    conversion_rate: float = None
    notes: str = None

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_engine():
    global engine
    if engine is None:
        engine = NeuroEngine()
    return engine

def run_inference_task(task_id: str, file_path: str, media_type: str, audience_params: dict):
    """Executes the heavy neural simulation and agent orchestration in the background."""
    db = SessionLocal()
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()

    if not task:
        logger.error(f"Task {task_id} not found in database.")
        db.close()
        return

    try:
        logger.info(f"Starting inference task: {task_id} for {media_type}")
        eng = get_engine()

        # 1. Neural Inference
        results = eng.analyze_media(file_path, media_type=media_type, audience_params=audience_params)

        # 2. Multi-Agent Orchestration (AaaS)
        logger.info(f"Running Multi-Agent orchestration for task: {task_id}")
        brain_report = brain.run_campaign_optimization(results, audience_params, media_type, file_path)

        # 3. Persistence
        task.results = results
        task.ai_advice = json.dumps(brain_report)
        task.status = "completed"
        db.commit()
        logger.info(f"Task {task_id} completed successfully.")

    except Exception as e:
        logger.error(f"Critical failure in background task {task_id}: {str(e)}", exc_info=True)
        try:
            task.status = "failed"
            # Optional: Store error details for debugging
            task.ai_advice = json.dumps({"error": str(e), "timestamp": str(datetime.now(UTC))})
            db.commit()
        except Exception as db_err:
            logger.error(f"Failed to update task status to 'failed': {str(db_err)}")
    finally:
        db.close()

@app.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = get_password_hash(user.password)
    # Security: Defaulting to Marketer role to prevent privilege escalation
    new_user = User(username=user.username, hashed_password=hashed_pwd, role="Marketer")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "username": new_user.username}

@app.post("/auth/token", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/analyze", response_model=AnalysisResponse)
@limiter.limit("10/minute")
async def analyze_media(
    request: Request,
    background_tasks: BackgroundTasks,
    media_type: str,
    file: UploadFile = File(None),
    text_content: str = None,
    campaign_name: str = "Default Campaign",
    age: str = "25-34",
    platform: str = "Meta",
    industry: str = "D2C",
    awareness: str = "Cold",
    persona: str = None,
    current_user: User = Depends(require_marketer),
    db: Session = Depends(get_db)
):
    task_id = str(uuid.uuid4())

    # Campaign lookup or creation
    campaign = db.query(Campaign).filter(Campaign.name == campaign_name).first()
    if not campaign:
        campaign = Campaign(name=campaign_name)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

    file_path = None
    if media_type == "text" and text_content:
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}.txt")
        with open(file_path, "w") as f:
            f.write(text_content)
    elif media_type == "url" and text_content:
        file_path = text_content
    elif file:
        s_filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{s_filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        raise HTTPException(status_code=400, detail="Missing input")

    # Initial task entry with Audience Params
    new_task = AnalysisTask(
        id=task_id,
        campaign_id=campaign.id,
        media_type=media_type,
        file_path=file_path,
        audience_age=age,
        audience_platform=platform,
        audience_industry=industry,
        audience_awareness=awareness,
        persona_description=persona
    )
    db.add(new_task)
    db.commit()

    audience_params = {"age": age, "platform": platform, "industry": industry, "awareness": awareness, "persona": persona}
    background_tasks.add_task(run_inference_task, task_id, file_path, media_type, audience_params)
    return AnalysisResponse(task_id=task_id, status="processing")

@app.post("/analyze_batch")
@limiter.limit("10/minute")
async def analyze_batch(
    request: Request,
    background_tasks: BackgroundTasks,
    media_type: str,
    files: list[UploadFile] = File(...),
    campaign_name: str = "Batch Campaign",
    age: str = "25-34",
    platform: str = "Meta",
    industry: str = "D2C",
    awareness: str = "Cold",
    persona: str = None,
    current_user: User = Depends(require_marketer),
    db: Session = Depends(get_db)
):
    task_ids = []

    campaign = db.query(Campaign).filter(Campaign.name == campaign_name).first()
    if not campaign:
        campaign = Campaign(name=campaign_name)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

    audience_params = {"age": age, "platform": platform, "industry": industry, "awareness": awareness, "persona": persona}

    for file in files:
        task_id = str(uuid.uuid4())
        s_filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{s_filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_task = AnalysisTask(
            id=task_id,
            campaign_id=campaign.id,
            media_type=media_type,
            file_path=file_path,
            audience_age=age,
            audience_platform=platform,
            audience_industry=industry,
            audience_awareness=awareness,
            persona_description=persona
        )
        db.add(new_task)
        task_ids.append(task_id)
        background_tasks.add_task(run_inference_task, task_id, file_path, media_type, audience_params)

    db.commit()
    return {"task_ids": task_ids, "status": "processing"}

@app.post("/generate_hooks")
@limiter.limit("20/minute")
async def generate_hooks(request: Request, product_desc: str, age: str, platform: str, industry: str, current_user: User = Depends(require_marketer)):
    audience_params = {"age": age, "platform": platform, "industry": industry}
    hooks = brain.strategist._generate(f"Generate 5 high-performance hooks for: {product_desc} targeting {json.dumps(audience_params)}")
    return {"hooks": hooks}

@app.get("/results/{task_id}")
async def get_results(task_id: str, current_user: User = Depends(require_viewer), db: Session = Depends(get_db)):
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    marketing_result = db.query(MarketingResult).filter(MarketingResult.task_id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.id,
        "status": task.status,
        "media_type": task.media_type,
        "audience": {
            "age": task.audience_age,
            "platform": task.audience_platform,
            "industry": task.audience_industry,
            "awareness": task.audience_awareness,
            "persona": task.persona_description
        },
        "data": task.results,
        "ai_advice": task.ai_advice,
        "marketing_actuals": {
            "ctr": marketing_result.ctr if marketing_result else None,
            "cpa": marketing_result.cpa if marketing_result else None
        } if marketing_result else None
    }

@app.post("/submit_results")
async def submit_marketing_results(res: MarketingResultIn, current_user: User = Depends(require_marketer), db: Session = Depends(get_db)):
    new_res = MarketingResult(
        task_id=res.task_id,
        ctr=res.ctr,
        cpc=res.cpc,
        cpa=res.cpa,
        conversion_rate=res.conversion_rate,
        notes=res.notes
    )
    db.add(new_res)
    db.commit()
    return {"status": "success"}

@app.get("/campaigns")
async def get_campaigns(current_user: User = Depends(require_viewer), db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    res = []
    for c in campaigns:
        tasks = db.query(AnalysisTask).filter(AnalysisTask.campaign_id == c.id).all()
        res.append({
            "id": c.id,
            "name": c.name,
            "task_count": len(tasks)
        })
    return res

@app.post("/chat/{task_id}")
@limiter.limit("20/minute")
async def chat_with_neuro(request: Request, task_id: str, query: str, current_user: User = Depends(require_marketer), db: Session = Depends(get_db)):
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()

    if not task or task.status != "completed":
        raise HTTPException(status_code=400, detail="Results not ready for chat")

    prompt = f"Using this neurological data: {json.dumps(task.results)}, answer this user query: {query}"
    response = brain.strategist._generate(prompt)
    return {"response": response}

@app.get("/health")
async def health(current_user: User = Depends(require_admin)):
    return {"status": "Pro 10x engine is active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
