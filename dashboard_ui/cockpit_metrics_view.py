# 📊 cockpit_metrics_view.py — Audit technique cockpit
import json
import streamlit as st
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd
import plotly.express as px

class CockpitMetricsManager:
    def __init__(self, yaml_path=None, session_state=None):
        self.paths = yaml_path if yaml_path else []
        self.session = session_state if session_state is not None else {}
        self.data_list = []

    def load(self, files=None):
        self.data_list.clear()
        file_sources = files if files else [Path(p) for p in self.paths]
        for f in file_sources:
            try:
                content = f.read() if hasattr(f, "read") else Path(f).read_text(encoding="utf-8")
                data = yaml.safe_load(content.decode("utf-8") if hasattr(f, "read") else content) or {}
                self.data_list.append(data)
            except Exception as e:
                st.warning(f"⚠️ Fichier non chargé : {f}\n{e}")
        self.session["metrics_yaml_multi"] = self.data_list

    def extract_series(self, key, label, scale=1.0):
        return [
            pd.DataFrame([
                {"timestamp": e.get("label", "t0"), label: float(e.get("value", ["", "0"])[1]) * scale}
                for e in data.get(key, []) if isinstance(e, dict)
            ])
            for data in self.data_list
        ]

    def get_latest(self, key):
        for data in reversed(self.data_list):
            if key in data:
                return data[key]
        return None

# === 🧭 Page cockpit
st.set_page_config(page_title="📊 Audit cockpit Oliplus", page_icon="🛠️", layout="wide")
st.title("🧭 Audit technique cockpit — KPI et monitoring")

uploaded_files = st.file_uploader("📁 Uploader fichiers YAML cockpit", type=["yaml", "yml"], accept_multiple_files=True)
metrics = CockpitMetricsManager(session_state=st.session_state)
if uploaded_files:
    metrics.load(files=uploaded_files)

cpu_dfs = metrics.extract_series("cpu_usage", "CPU (sec)")
ram_dfs = metrics.extract_series("memory_rss", "RAM (MB)", scale=1 / 1_000_000)

latest_cpu = max([df.iloc[-1]["CPU (sec)"] for df in cpu_dfs if not df.empty], default=0.0)
latest_ram = max([df.iloc[-1]["RAM (MB)"] for df in ram_dfs if not df.empty], default=0.0)
archives = metrics.get_latest("archives_processed") or 0
anomalies = metrics.get_latest("anomalies") or 0
roadmap = metrics.get_latest("roadmap_progress") or 0
warnings = metrics.get_latest("warnings") or []

# === 🔎 Navigation cockpit
tab1, tab2, tab3 = st.tabs(["📌 Indicateurs", "📊 Visualisations", "📬 Avertissements"])

with tab1:
    st.subheader("📌 Indicateurs cockpit")
    col1, col2, col3 = st.columns(3)
    col1.metric("🧠 CPU max", f"{latest_cpu:.2f} sec")
    col1.progress(min(latest_cpu / 80.0, 1.0))
    col2.metric("💾 RAM max", f"{latest_ram:.2f} MB")
    col2.progress(min(latest_ram / 100.0, 1.0))
    col3.metric("📦 Archives", archives)
    col3.progress(min(archives / 100.0, 1.0))

    if roadmap:
        st.info(f"📍 Roadmap : `{roadmap}%`")
        st.progress(roadmap / 100.0)

    st.subheader("🚨 Anomalies")
    if anomalies > 0:
        st.warning(f"`{anomalies}` anomalies détectées")
    else:
        st.success("✅ Aucun incident")

with tab2:
    st.subheader("📊 Charge CPU / RAM")
    sub1, sub2 = st.tabs(["🧠 CPU", "📊 RAM"])
    with sub1:
        for idx, df in enumerate(cpu_dfs):
            if not df.empty:
                st.plotly_chart(px.line(df, x="timestamp", y="CPU (sec)", title=f"CPU {idx+1}"), use_container_width=True)
    with sub2:
        for idx, df in enumerate(ram_dfs):
            if not df.empty:
                st.plotly_chart(px.line(df, x="timestamp", y="RAM (MB)", title=f"RAM {idx+1}"), use_container_width=True)

with tab3:
    st.subheader("📬 Avertissements")
    query = st.text_input("🔍 Filtrer par mot-clé")
    filtered = [w for w in warnings if query.lower() in w.lower()] if query else warnings
    for w in filtered:
        st.markdown(f"- ⚠️ `{w}`")

st.caption(f"🕒 Tableau cockpit généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.toast("✅ Vue technique cockpit mise à jour", icon="🛠️")
