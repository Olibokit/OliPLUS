# 📘 document_dashboard_view.py — Vue cockpit Streamlit pour exploration documentaire typée

import streamlit as st
import pandas as pd
import json
import yaml
import random
from datetime import datetime, timedelta
from collections import Counter

# === Configuration de la page cockpitifiée ===
st.set_page_config(
    page_title="📄 Tableau de bord documentaire Cockpit",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📘 Tableau de bord documentaire Cockpit")
st.markdown("Explorez, filtrez et exportez vos artefacts injectés dans le système cockpit.")

# === Chargement cockpit simulé des documents ===
@st.cache_data(ttl=120)
def load_simulated_documents():
    types = ["Rapport", "Facture", "Contrat", "Image", "Présentation"]
    authors = ["Jean Dupont", "Marie Curie", "Pierre Martin", "Alice Wonderland"]
    statuses = ["Traité", "En attente", "Erreur", "Archivé"]
    tags_pool = ["finance", "RH", "projetX", "clientA", "interne", "urgent"]

    data = []
    for i in range(1, 101):
        selected_tags = random.sample(tags_pool, k=random.randint(1, 3))
        data.append({
            "ID Document": f"doc-{i:04d}",
            "Titre": f"{random.choice(types)} cockpit n°{i}",
            "Type": random.choice(types),
            "Auteur": random.choice(authors),
            "Statut": random.choice(statuses),
            "Tags": selected_tags,
            "Date d'Injection": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "Taille (Ko)": random.randint(100, 5000)
        })
    return pd.DataFrame(data)

df_docs = load_simulated_documents()

# === Sidebar cockpitifiée : filtres ===
st.sidebar.header("🎛️ Filtres cockpit")

type_filter = st.sidebar.selectbox("Type de document", ["Tous"] + sorted(df_docs["Type"].unique()))
author_filter = st.sidebar.selectbox("Auteur", ["Tous"] + sorted(df_docs["Auteur"].unique()))
status_filter = st.sidebar.selectbox("Statut", ["Tous"] + sorted(df_docs["Statut"].unique()))
tags_flat = sorted(list(set(tag for tag_list in df_docs["Tags"] for tag in tag_list)))
tags_filter = st.sidebar.multiselect("Tags", tags_flat)
search_query = st.sidebar.text_input("🔍 Recherche (titre ou ID)").lower().strip()

# === Application des filtres typés ===
filtered = df_docs.copy()

if type_filter != "Tous":
    filtered = filtered[filtered["Type"] == type_filter]

if author_filter != "Tous":
    filtered = filtered[filtered["Auteur"] == author_filter]

if status_filter != "Tous":
    filtered = filtered[filtered["Statut"] == status_filter]

if tags_filter:
    filtered = filtered[
        filtered["Tags"].apply(lambda tags: any(tag in tags for tag in tags_filter))
    ]

if search_query:
    filtered = filtered[
        filtered.apply(lambda row: search_query in row["Titre"].lower() or search_query in row["ID Document"].lower(), axis=1)
    ]

# === Tableau cockpit documenté ===
st.header("📋 Documents filtrés")
if not filtered.empty:
    df_display = filtered.copy()
    df_display["Tags"] = df_display["Tags"].apply(lambda x: ", ".join(x))
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    st.markdown(f"**📊 Nombre total affiché :** {len(filtered)}")
else:
    st.warning("📭 Aucun document ne correspond aux filtres appliqués.")

# === Statistiques typées cockpit ===
st.markdown("---")
st.header("📈 Statistiques documentaires")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("📦 Documents injectés", len(df_docs))
with c2:
    st.metric("🔍 Résultats filtrés", len(filtered))
with c3:
    st.metric("📁 Types uniques", len(df_docs["Type"].unique()))

st.subheader("🗂️ Répartition par Type")
st.bar_chart(filtered["Type"].value_counts())

st.subheader("📌 Répartition par Statut")
st.bar_chart(filtered["Statut"].value_counts())

st.subheader("📅 Histogramme des dates d'injection")
filtered["Date d'Injection"] = pd.to_datetime(filtered["Date d'Injection"])
date_hist = filtered["Date d'Injection"].dt.to_period("M").value_counts().sort_index()
st.bar_chart(date_hist)

st.subheader("🏷️ Nuage de tags")
tag_counter = Counter(tag for tags in filtered["Tags"] for tag in tags)
tag_df = pd.DataFrame(tag_counter.items(), columns=["Tag", "Occurrences"]).sort_values(by="Occurrences", ascending=False)
st.dataframe(tag_df, use_container_width=True)

# === Export cockpit enrichi ===
st.markdown("---")
st.subheader("📤 Export des documents filtrés")
export_format = st.selectbox("Format d'export", ["CSV", "YAML"])

if not filtered.empty:
    if export_format == "CSV":
        csv_bytes = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Télécharger en CSV",
            data=csv_bytes,
            file_name="documents_filtrés.csv",
            mime="text/csv"
        )
    elif export_format == "YAML":
        yaml_data = yaml.dump(filtered.to_dict(orient="records"), allow_unicode=True)
        st.download_button(
            label="📥 Télécharger en YAML",
            data=yaml_data.encode("utf-8"),
            file_name="documents_filtrés.yaml",
            mime="text/yaml"
        )
