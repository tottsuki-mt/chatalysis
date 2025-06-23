# app.py – Chat & Audio input (Enter 送信 + 入力欄クリア対応版)
# -----------------------------------------------------------------------------
import io
import logging
import os
import traceback
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.llms import Ollama

try:
    from llm_logger import logger
except ImportError:  # ロガーが無くても動くように
    logger = logging.getLogger(__name__)

# ------------------------------ ENV ------------------------------------------
load_dotenv()
ALLOW_DANGER = os.getenv("ALLOW_DANGEROUS_CODE", "false").lower() == "true"
WHISPER_URL = os.getenv("WHISPER_URL", "http://localhost:8000/v1/audio/transcriptions")


# --------------------------- LLM / Whisper -----------------------------------
@st.cache_resource(show_spinner="LLM をロード中…")
def load_llm():
    return Ollama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:14b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7,
        top_p=0.95,
        top_k=20,
    )


def whisper_transcribe(audio_bytes: bytes, mime="audio/webm", lang="ja") -> str:
    files = {"file": ("audio.webm", audio_bytes, mime)}
    data = {"model": os.getenv("WHISPER_MODEL", "whisper-1"), "language": lang}
    try:
        r = requests.post(WHISPER_URL, files=files, data=data, timeout=90)
        r.raise_for_status()
        return r.json().get("text", "").strip()
    except Exception as e:
        st.error(f"Whisper API エラー: {e}")
        return ""


# ----------------------------- Utility ---------------------------------------
def _execute_code(code: str) -> None:
    """Execute Python code safely and render matplotlib figures."""
    exec(code, {}, {"df": st.session_state.df, "pd": pd, "st": st, "plt": plt})
    for fig_num in plt.get_fignums():
        fig = plt.figure(fig_num)
        if fig.axes:
            st.pyplot(fig, clear_figure=False)
        plt.close(fig)


def _extract_python_blocks(text: str) -> List[str]:
    """Return Python code blocks contained in markdown text."""
    if "```python" not in text:
        return []
    blocks: List[str] = []
    for block in text.split("```python")[1:]:
        blocks.append(block.split("```", 1)[0])
    return blocks


def _strip_think_tags(text: str) -> str:
    """Remove <think>...</think> sections from text."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


# ------------------------- Matplotlib → Streamlit ----------------------------
def _streamlit_show(*_, **__):
    fig = plt.gcf()  # 現在のフィギュアを取得
    # フィギュアに何か描画されているか確認 (軸が存在するかどうか)
    if fig.axes:
        st.pyplot(fig, clear_figure=False)  # Streamlitで表示
    plt.close(
        fig
    )  # 表示後、Matplotlib側でフィギュアを閉じる (プロット内容の有無に関わらず)


plt.show = _streamlit_show  # plt.show() を上書き

# ------------------------------- UI ------------------------------------------
st.set_page_config(page_title="Chat Data Analyst", layout="wide")
st.title("📊 Chat Data Analyst (demo)")

uploaded = st.sidebar.file_uploader("🔼 データをアップロード", ["csv", "xlsx", "json"])

if "df" not in st.session_state:
    st.session_state.df = None
if uploaded:
    if uploaded.type.endswith("spreadsheetml.sheet"):
        st.session_state.df = pd.read_excel(uploaded)
    elif uploaded.type.endswith("json"):
        st.session_state.df = pd.read_json(uploaded)
    else:
        st.session_state.df = pd.read_csv(uploaded)
    st.success(
        f"{len(st.session_state.df):,} 行 × {len(st.session_state.df.columns)} 列 を読み込みました。"
    )
    st.dataframe(st.session_state.df.head(), height=250)

# -------------------------- Pandas-Agent -------------------------------------
if "agent" not in st.session_state and st.session_state.df is not None:
    with st.spinner("エージェント初期化中…"):
        st.session_state.agent = create_pandas_dataframe_agent(
            load_llm(),
            st.session_state.df,
            prefix=(
                "あなたは優秀なデータサイエンティストです。"
                "Python (pandas / matplotlib / seaborn / plotly) で回答し、"
                "コードは ```python``` で囲んでください。"
            ),
            verbose=True,
            allow_dangerous_code=ALLOW_DANGER,
        )
        st.session_state.messages = []
        st.session_state.draft = ""

# --------------------------- Chat Loop ---------------------------------------
st.divider()
chat_box = st.container()

# ---- 既存メッセージの描画 ----
for msg in st.session_state.get("messages", []):
    with chat_box.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("code_blocks"):
            for code in msg["code_blocks"]:
                try:
                    _execute_code(code)
                except Exception as e:
                    st.error(f"再実行失敗: {e}")
                    traceback.print_exc()  # エラーの詳細を出力

# --------------------------- 入力 UI -----------------------------------------
if st.session_state.get("agent"):

    col_txt, col_mic, col_send = st.columns([9, 1, 1])

    if "send_enter" not in st.session_state:
        st.session_state.send_enter = False

    def _enter_pressed():
        st.session_state.send_enter = True

    user_text = col_txt.text_input(
        "質問を入力…",
        value=st.session_state.draft,
        label_visibility="collapsed",
        key="chat_input",
        on_change=_enter_pressed,
    )

    with col_mic:
        audio_dict = mic_recorder(
            "🎙️", "■", key="rec_btn", just_once=True, use_container_width=True
        )

    send_clicked = col_send.button("➤", use_container_width=True)
    send_triggered = send_clicked or st.session_state.pop("send_enter", False)

    # -------------- 音声入力処理 ----------------
    if audio_dict and audio_dict.get("bytes"):
        transcript = whisper_transcribe(audio_dict["bytes"])
        if transcript:
            st.session_state.draft = transcript
            st.toast(f"🎤 音声入力: {transcript}", icon="🎙️")
            st.rerun()

    # -------------- 送信処理 --------------------
    q = None
    if send_triggered and user_text.strip():
        q = user_text.strip()
        st.session_state.draft = ""  # 入力欄クリア

    # -------------- LLM 呼び出し -----------------
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        with chat_box.chat_message("user"):
            st.markdown(q)

        with chat_box.chat_message("assistant"):
            with st.spinner("考え中…"):
                try:
                    logger.info(f"[LLM INPUT] {q}")
                    resp = st.session_state.agent.invoke({"input": q})["output"]
                    resp = _strip_think_tags(resp)
                    logger.info(f"[LLM OUTPUT] {resp}")
                except Exception as e:
                    traceback.print_exc()
                    resp = f"⚠️ エラー: {e}"
                st.markdown(resp)

                # ---------- コードブロック実行 ----------
                code_blocks = _extract_python_blocks(resp)
                if ALLOW_DANGER:
                    for code in code_blocks:
                        try:
                            _execute_code(code)
                        except Exception as e:
                            st.error(f"コード実行失敗: {e}")
                            traceback.print_exc()  # エラーの詳細を出力

        # ---------- メッセージ履歴へ保存 ----------
        st.session_state.messages.append(
            {"role": "assistant", "content": resp, "code_blocks": code_blocks}
        )
else:
    st.info("まずはデータファイルをアップロードしてください。")
