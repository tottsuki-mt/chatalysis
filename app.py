# app.py – Chat & Audio input (Enter 送信 + 入力欄クリア対応版)
# ---------------------------------------------------------------------------
import io, os, traceback, logging, hashlib
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import requests, streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.llms import Ollama

try:
    from llm_logger import logger
except ImportError:
    logger = logging.getLogger(__name__)

# ------------------------------ ENV ----------------------------------------
load_dotenv()
ALLOW_DANGER = os.getenv("ALLOW_DANGEROUS_CODE", "false").lower() == "true"
WHISPER_URL  = os.getenv("WHISPER_URL", "http://localhost:8000/v1/audio/transcriptions")

# --------------------------- LLM / Whisper ---------------------------------
@st.cache_resource(show_spinner="LLM をロード中…")
def load_llm():
    return Ollama(
        model=os.getenv("OLLAMA_MODEL", "qwen3:14b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7, top_p=0.95, top_k=20,
    )

def whisper_transcribe(audio_bytes: bytes, mime="audio/webm", lang="ja") -> str:
    files = {"file": ("audio.webm", audio_bytes, mime)}
    data  = {"model": os.getenv("WHISPER_MODEL", "whisper-1"), "language": lang}
    try:
        r = requests.post(WHISPER_URL, files=files, data=data, timeout=90)
        r.raise_for_status()
        return r.json().get("text", "").strip()
    except Exception as e:
        st.error(f"Whisper API エラー: {e}")
        return ""

# ------------------------- Matplotlib → Streamlit --------------------------
# def _streamlit_show(...):  <-- この関数を削除
# plt.show = _streamlit_show  <-- この行を削除

# -------------------------- Code-Exec Cache --------------------------------
if "exec_cache" not in st.session_state:
    # code_hash ➜ {"fig_bytes": [...], "plotly_jsons": [...]} 
    st.session_state.exec_cache = {}

def run_code_once(code: str, show: bool = True) -> tuple[list[bytes], list[str]]:
    code_hash = hashlib.md5(code.encode("utf-8")).hexdigest()
    cache = st.session_state.exec_cache.get(code_hash)

    if cache:
        if show:
            for buf in cache["fig_bytes"]:
                st.image(buf, use_column_width=True)
            for js in cache.get("plotly_jsons", []):
                st.plotly_chart(pio.from_json(js), use_container_width=True)
        return cache["fig_bytes"], cache.get("plotly_jsons", [])

    local_ctx = {
        "df": st.session_state.df,
        "pd": pd,
        "st": st,
        "plt": plt,
        "go": go,
        "px": px,
    }

    plotly_figs: list[go.Figure] = []

    def _pio_show(fig, *_, **__):
        plotly_figs.append(fig)

    orig_show = pio.show
    pio.show = _pio_show
    try:
        exec(code, {}, local_ctx)  # LLMは plt.show()/fig.show() を呼ばない前提
    finally:
        pio.show = orig_show

    # local variables から Plotly Figure を収集
    for val in local_ctx.values():
        if isinstance(val, go.Figure) and val not in plotly_figs:
            plotly_figs.append(val)

    fig_bytes: list[bytes] = []
    for num in plt.get_fignums():
        fig = plt.figure(num)

        # 1. PNGデータを生成 (st.pyplot(clear_figure=True) の前に)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        fig_bytes.append(buf.getvalue())

        # 2. Streamlitで表示 (show=True の場合)
        if show:
            st.pyplot(fig, clear_figure=True)  # ここで表示し、Figureをクリア

        # 3. MatplotlibのFigureを閉じる
        plt.close(fig)

    plotly_jsons: list[str] = []
    for fig in plotly_figs:
        plotly_jsons.append(pio.to_json(fig))
        if show:
            st.plotly_chart(fig, use_container_width=True)

    st.session_state.exec_cache[code_hash] = {
        "fig_bytes": fig_bytes,
        "plotly_jsons": plotly_jsons,
    }
    return fig_bytes, plotly_jsons

# ------------------------------- UI ----------------------------------------
st.set_page_config(page_title="Chat Data Analyst", layout="wide")
st.title("📊 Chat Data Analyst (demo)")

uploaded = st.sidebar.file_uploader("🔼 データをアップロード", ["csv", "xlsx", "json"])

if "df" not in st.session_state:
    st.session_state.df = None
if uploaded:
    if uploaded.type.endswith("spreadsheetml.sheet"): # .xlsx
        st.session_state.df = pd.read_excel(uploaded)
    elif uploaded.type.endswith("json"): # .json
        st.session_state.df = pd.read_json(uploaded)
    else: # .csv
        st.session_state.df = pd.read_csv(uploaded)
    st.success(f"{len(st.session_state.df):,} 行 × {len(st.session_state.df.columns)} 列 を読み込みました。")
    st.dataframe(st.session_state.df.head(), height=250)

# -------------------------- Pandas-Agent -----------------------------------
if "agent" not in st.session_state and st.session_state.df is not None:
    with st.spinner("エージェント初期化中…"):
        st.session_state.agent = create_pandas_dataframe_agent(
            load_llm(),
            st.session_state.df,
            prefix=(
                "あなたは優秀なデータサイエンティストです。"
                "Python (pandas / matplotlib / seaborn / plotly) で回答し、"
                "コードは ```python``` で囲んでください。"
                "グラフを生成する際は plt.show() を呼び出さないでください。" # <--- 指示を追加
            ),
            verbose=True,
            allow_dangerous_code=ALLOW_DANGER,
        )
        st.session_state.messages = []
        st.session_state.draft    = ""

# --------------------------- Chat Loop -------------------------------------
st.divider()
chat_box = st.container()

# ---- 既存メッセージの描画 ----
for msg in st.session_state.get("messages", []):
    with chat_box.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 旧グラフは保存済み PNG / Plotly JSON を再描画
        for buf in msg.get("fig_bytes", []):
            st.image(buf, use_column_width=True)
        for js in msg.get("plotly_jsons", []):
            st.plotly_chart(pio.from_json(js), use_container_width=True)

# --------------------------- 入力 UI ---------------------------------------
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
        audio_dict = mic_recorder("🎙️", "■", key="rec_btn",
                                  just_once=True, use_container_width=True)

    send_clicked   = col_send.button("➤", use_container_width=True)
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
        st.session_state.draft = ""          # 入力欄クリア

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
                    logger.info(f"[LLM OUTPUT] {resp}")
                except Exception as e:
                    traceback.print_exc()
                    resp = f"⚠️ エラー: {e}"
                st.markdown(resp)

                # ---------- コードブロック実行 ----------
                code_blocks, fig_bytes_all, plotly_jsons_all = [], [], []
                if "```python" in resp and ALLOW_DANGER:
                    for block in resp.split("```python")[1:]:
                        code = block.split("```", 1)[0]
                        code_blocks.append(code)
                        imgs, js = run_code_once(code)
                        fig_bytes_all.extend(imgs)
                        plotly_jsons_all.extend(js)

        # ---------- メッセージ履歴へ保存 ----------
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": resp,
                "code_blocks": code_blocks,
                "fig_bytes": fig_bytes_all,
                "plotly_jsons": plotly_jsons_all,
            }
        )
else:
    st.info("まずはデータファイルをアップロードしてください。")