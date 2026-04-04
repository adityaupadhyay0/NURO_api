from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel
import shutil
import os
import uuid
import json
from datetime import datetime
from neuro_engine import NeuroEngine
from ai_consultant import GeminiConsultant
from database import SessionLocal, AnalysisTask, Campaign

app = FastAPI(title="NeuroMark Pro 10x API")

# Global instances
engine = None
consultant = GeminiConsultant() # API Key from env

UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

class AnalysisResponse(BaseModel):
    task_id: str
    status: str

def get_engine():
    global engine
    if engine is None:
        engine = NeuroEngine()
    return engine

def run_inference_task(task_id: str, file_path: str, media_type: str):
    db = SessionLocal()
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()

    try:
        eng = get_engine()
        results = eng.analyze_media(file_path, media_type=media_type)

        # 10x Enhanced: Get Strategic AI Advice from Gemini
        ai_advice = consultant.get_strategic_advice(results)

        # Update Database
        task.results = results
        task.ai_advice = ai_advice
        task.status = "completed"
        db.commit()

    except Exception as e:
        print(f"Error in task {task_id}: {e}")
        task.status = "failed"
        db.commit()
    finally:
        db.close()

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_media(
    background_tasks: BackgroundTasks,
    media_type: str,
    file: UploadFile = File(None),
    text_content: str = None,
    campaign_name: str = "Default Campaign"
):
    task_id = str(uuid.uuid4())
    db = SessionLocal()

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
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        db.close()
        raise HTTPException(status_code=400, detail="Missing input")

    # Initial task entry
    new_task = AnalysisTask(
        id=task_id,
        campaign_id=campaign.id,
        media_type=media_type,
        file_path=file_path
    )
    db.add(new_task)
    db.commit()
    db.close()

    background_tasks.add_task(run_inference_task, task_id, file_path, media_type)
    return AnalysisResponse(task_id=task_id, status="processing")

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    db = SessionLocal()
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    db.close()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.id,
        "status": task.status,
        "media_type": task.media_type,
        "data": task.results,
        "ai_advice": task.ai_advice
    }

@app.get("/campaigns")
async def get_campaigns():
    db = SessionLocal()
    campaigns = db.query(Campaign).all()
    res = []
    for c in campaigns:
        tasks = db.query(AnalysisTask).filter(AnalysisTask.campaign_id == c.id).all()
        res.append({
            "id": c.id,
            "name": c.name,
            "task_count": len(tasks)
        })
    db.close()
    return res

@app.post("/chat/{task_id}")
async def chat_with_neuro(task_id: str, query: str):
    db = SessionLocal()
    task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
    db.close()

    if not task or task.status != "completed":
        raise HTTPException(status_code=400, detail="Results not ready for chat")

    response = consultant.chat_with_neuro_data(query, task.results)
    return {"response": response}

@app.get("/health")
async def health():
    return {"status": "Pro 10x engine is active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
