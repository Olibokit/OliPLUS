import streamlit as st
import pandas as pd
import yaml
import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")

def load_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement CSV : {e}")
        return pd.DataFrame()

def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        st.error(f"❌ Erreur YAML cockpit : {e}")
        return {}

def load_markdown(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"❌ Erreur Markdown cockpit : {e}")
        return ""

def render_yaml_tree(data: Any, level: int = 0) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            with st.expander(f"{'📁 ' * level}{key}", expanded=False):
                render_yaml_tree(value, level + 1)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            with st.expander(f"{'📄 ' * level}Item {i+1}", expanded=False):
                render_yaml_tree(item, level + 1)
    else:
        st.write(data)

def render() -> None:
    st.set_page_config(page_title="Classification cockpit", page_icon="📂", layout="wide")
    st.title("📂 Plan de classement documentaire cockpit Oliplus")

    st.markdown(
        """
        Plateforme cockpit typée pour visualiser les plans de classement sous trois formes :
        - 🔍 Recherche CSV cockpitifiée
        - 📤 Export JSON cockpit
        - 🧩 Vue interactive YAML cockpit
        """
    )
    st.divider()

    tab_csv, tab_yaml, tab_md = st.tabs(["📄 CSV cockpit", "🧬 YAML structure", "📝 Markdown"])

    # 📄 Vue CSV cockpitifiée avec recherche
    with tab_csv:
        csv_file = DATA_DIR / "classification_export.csv"
        if csv_file.exists():
            df = load_csv(csv_file)
            st.subheader("📊 Tableau cockpit")
            search_term = st.text_input("🔍 Rechercher dans le tableau", "")
            if search_term:
                filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"⚠️ Fichier CSV introuvable : `{csv_file}`")

    # 🧬 Vue YAML cockpitifiée interactive + export JSON
    with tab_yaml:
        yaml_file = DATA_DIR / "classification_plan.yaml"
        if yaml_file.exists():
            structure = load_yaml(yaml_file)
            st.subheader("🧬 Arborescence interactive cockpit")
            render_yaml_tree(structure)

            st.subheader("📤 Export JSON cockpit")
            json_str = json.dumps(structure, indent=2, ensure_ascii=False)
            st.download_button("📥 Télécharger JSON", data=json_str, file_name="classification_plan.json", mime="application/json")
        else:
            st.warning(f"⚠️ Fichier YAML introuvable : `{yaml_file}`")

    # 📝 Vue Markdown cockpitifiée
    with tab_md:
        md_path = DATA_DIR / "classification_export.md"
        if md_path.exists():
            content = load_markdown(md_path)
            st.subheader("📝 Aperçu Markdown cockpit")
            st.markdown(content, unsafe_allow_html=False)
        else:
            st.info(f"ℹ️ Fichier Markdown non trouvé : `{md_path}` — export à régénérer")

# ✅ Intégration cockpit recommandée :
# from classification_cockpit import render
# render()
