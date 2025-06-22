import os
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.llms import Ollama

load_dotenv()
WHISPER_URL = os.getenv("WHISPER_URL", "http://localhost:8000/v1/audio/transcriptions")

@st.cache_resource(show_spinner="LLM をロード中…")
def load_llm():
    return Ollama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:14b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7,
        top_p=0.95,
        top_k=20,
    )

def whisper_transcribe(audio_bytes: bytes, mime: str = "audio/webm", lang: str = "ja") -> str:
    files = {"file": ("audio.webm", audio_bytes, mime)}
    data = {"model": os.getenv("WHISPER_MODEL", "whisper-1"), "language": lang}
    try:
        r = requests.post(WHISPER_URL, files=files, data=data, timeout=90)
        r.raise_for_status()
        return r.json().get("text", "").strip()
    except Exception as e:
        st.error(f"Whisper API エラー: {e}")
        return ""
