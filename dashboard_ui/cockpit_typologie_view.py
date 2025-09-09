# 📘 cockpit_typologie_view.py — Navigation typologique cockpitifiée
import streamlit as st
import yaml
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="📘 Typologie cockpitifiée", page_icon="🧩", layout="wide")
st.title("🧩 Navigation typologique cockpit — Référentiel YAML")

# 📁 Chargement du fichier YAML
uploaded_file = st.file_uploader("📁 Charger un fichier de typologie cockpitifiée (.yaml)", type=["yaml", "yml"])
if uploaded_file:
    try:
        content = uploaded_file.read().decode("utf-8")
        data = yaml.safe_load(content)
    except Exception as e:
        st.error(f"❌ Erreur de chargement : {e}")
        st.stop()
else:
    st.info("📘 En attente d’un fichier YAML cockpitifié…")
    st.stop()

# 📊 Extraction des blocs typologiques
segments = data.get("typologies", [])
df = pd.DataFrame(segments)

# 🔍 Filtres cockpitifiés
st.sidebar.header("🔍 Filtres cockpit")
domaines = st.sidebar.multiselect("📂 Domaine", options=df["domaine"].unique())
codes = st.sidebar.multiselect("🆔 Code", options=df["code"].unique())
roles = st.sidebar.multiselect("🎯 Rôle", options=df["rôle"].unique())

filtered_df = df.copy()
if domaines:
    filtered_df = filtered_df[filtered_df["domaine"].isin(domaines)]
if codes:
    filtered_df = filtered_df[filtered_df["code"].isin(codes)]
if roles:
    filtered_df = filtered_df[filtered_df["rôle"].isin(roles)]

# 📘 Affichage cockpitifié
tab1, tab2 = st.tabs(["📋 Tableau typologique", "📊 Graphe par domaine"])

with tab1:
    st.subheader("📋 Typologies cockpitifiées")
    st.dataframe(filtered_df, use_container_width=True)

with tab2:
    if not filtered_df.empty:
        fig = px.bar(filtered_df, x="domaine", color="rôle", title="Répartition typologique par domaine")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ Aucun segment à afficher")

# 📦 Résumé cockpit
st.caption(f"📘 {len(filtered_df)} segment(s) typologiques affichés — fichier : `{uploaded_file.name}`")
