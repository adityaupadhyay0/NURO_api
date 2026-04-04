from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel
import shutil
import os
import uuid
import json
from datetime import datetime
from neuro_engine import NeuroEngine

app = FastAPI(title="NeuroMark SaaS API")

# Global engine instance (Lazy loaded for production)
engine = None

UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

class AnalysisRequest(BaseModel):
    media_type: str  # 'video', 'audio', 'text'
    text_content: str = None

class AnalysisResponse(BaseModel):
    task_id: str
    status: str

def get_engine():
    global engine
    if engine is None:
        engine = NeuroEngine()
    return engine

def run_inference_task(task_id: str, file_path: str, media_type: str):
    try:
        eng = get_engine()
        results = eng.analyze_media(file_path, media_type=media_type)

        # Save results to JSON
        result_path = os.path.join(RESULTS_DIR, f"{task_id}.json")
        with open(result_path, "w") as f:
            json.dump({
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "media_type": media_type,
                "data": results
            }, f)

        # Update status in a simple way (for MVP)
        status_path = os.path.join(RESULTS_DIR, f"{task_id}_status.json")
        with open(status_path, "w") as f:
            json.dump({"status": "completed"}, f)

    except Exception as e:
        print(f"Error in task {task_id}: {e}")
        status_path = os.path.join(RESULTS_DIR, f"{task_id}_status.json")
        with open(status_path, "w") as f:
            json.dump({"status": "failed", "error": str(e)}, f)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_media(
    background_tasks: BackgroundTasks,
    media_type: str,
    file: UploadFile = File(None),
    text_content: str = None
):
    task_id = str(uuid.uuid4())
    file_path = None

    if media_type == "text" and text_content:
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}.txt")
        with open(file_path, "w") as f:
            f.write(text_content)
    elif media_type == "url" and text_content:
        # Use URL from text_content directly
        file_path = text_content
    elif file:
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        raise HTTPException(status_code=400, detail="Missing file or text content")

    # Initial status
    status_path = os.path.join(RESULTS_DIR, f"{task_id}_status.json")
    with open(status_path, "w") as f:
        json.dump({"status": "processing"}, f)

    background_tasks.add_task(run_inference_task, task_id, file_path, media_type)

    return AnalysisResponse(task_id=task_id, status="processing")

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    result_path = os.path.join(RESULTS_DIR, f"{task_id}.json")
    status_path = os.path.join(RESULTS_DIR, f"{task_id}_status.json")

    if not os.path.exists(status_path):
        raise HTTPException(status_code=404, detail="Task not found")

    with open(status_path, "r") as f:
        status_data = json.load(f)

    if status_data["status"] == "completed":
        with open(result_path, "r") as f:
            return json.load(f)

    return status_data

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
