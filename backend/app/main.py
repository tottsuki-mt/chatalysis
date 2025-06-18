from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Dict
from .agent import create_agent
from xinference import Client
from dotenv import load_dotenv
import tempfile
import os


load_dotenv()
app = FastAPI()

sessions: Dict[str, pd.DataFrame] = {}
agents: Dict[str, any] = {}

xinference_url = os.getenv("XINFERENCE_URL", "http://localhost:9997")
xinference_client = Client(xinference_url)
model_name = os.getenv("XINFERENCE_MODEL_NAME", "whisper")
model_size = os.getenv("XINFERENCE_MODEL_SIZE", "small")
model_uid = None

@app.on_event("startup")
async def startup_event():
    global model_uid
    try:
        model_uid = xinference_client.launch_model(model_name=model_name, model_size=model_size)
    except Exception:
        # assume already launched
        models = xinference_client.list_models()
        for uid, info in models.items():
            if info.get("model_name") == model_name:
                model_uid = uid
                break

@app.post("/api/upload")
async def upload_csv(session_id: str = Form(...), file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        sessions[session_id] = df
        agents[session_id] = create_agent(df)
        return {"status": "success", "columns": df.columns.tolist()}
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "detail": str(e)})

@app.post("/api/chat")
async def chat(session_id: str = Form(...), message: str = Form(...)):
    if session_id not in sessions:
        return JSONResponse(status_code=404, content={"status": "error", "detail": "Session not found"})
    try:
        agent = agents[session_id]
        reply = agent.run(message)
        return {"status": "success", "reply": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if model_uid is None:
        return JSONResponse(status_code=500, content={"status": "error", "detail": "Model not ready"})
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            resp = xinference_client.chat(model_uid, input=tmp.name)
        text = resp["text"] if isinstance(resp, dict) else resp
        return {"status": "success", "text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
