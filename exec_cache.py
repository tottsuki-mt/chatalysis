import hashlib
import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

if "exec_cache" not in st.session_state:
    st.session_state.exec_cache = {}

def run_code_once(code: str, show: bool = True) -> list[bytes]:
    code_hash = hashlib.md5(code.encode("utf-8")).hexdigest()
    cache = st.session_state.exec_cache.get(code_hash)

    if cache:
        if show:
            for buf in cache["fig_bytes"]:
                st.image(buf, use_column_width=True)
        return cache["fig_bytes"]

    local_ctx = {"df": st.session_state.df, "pd": pd, "st": st, "plt": plt}
    exec(code, {}, local_ctx)

    fig_bytes: list[bytes] = []
    for num in plt.get_fignums():
        fig = plt.figure(num)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        fig_bytes.append(buf.getvalue())
        if show:
            st.pyplot(fig, clear_figure=True)
        plt.close(fig)

    st.session_state.exec_cache[code_hash] = {"fig_bytes": fig_bytes}
    return fig_bytes
