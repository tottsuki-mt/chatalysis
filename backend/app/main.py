from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Dict
from .agent import create_agent
from dotenv import load_dotenv
import requests
import os


load_dotenv()
app = FastAPI()

sessions: Dict[str, pd.DataFrame] = {}
agents: Dict[str, any] = {}

xinference_url = os.getenv("XINFERENCE_URL", "http://localhost:9997")
whisper_url = os.getenv("WHISPER_URL", f"{xinference_url}/v1/audio/transcriptions")
whisper_model = os.getenv("XINFERENCE_MODEL", "whisper")


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
    try:
        content = await file.read()
        files = {"file": (file.filename, content, file.content_type)}
        data = {"model": whisper_model}
        resp = requests.post(whisper_url, files=files, data=data, timeout=90)
        resp.raise_for_status()
        text = resp.json().get("text", "").strip()
        return {"status": "success", "text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
