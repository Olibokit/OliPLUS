# 📘 dashboard_structure_view.py
# Interface cockpit pour explorer l’arborescence de oliPLUS_structure.txt

import streamlit as st
import os
import re

# --- Configuration Streamlit ---
st.set_page_config(
    page_title="Cockpit Structure Viewer",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧱 Vue Cockpit de la Structure OliPLUS")
st.markdown("Explorez et naviguez dans l'arborescence cockpitifiée du projet OliPLUS.")

# --- Fonction pour charger et parser le fichier .txt ---
@st.cache_data
def load_and_parse_structure(file_path):
    structure = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        line_pattern = re.compile(r"^(│\s{3}|├──\s|└──\s|\s{4})*(.*?)(?:(?:\r?\n)|$)")
        for line in lines:
            match = line_pattern.match(line)
            if match:
                indent_str = match.group(0).replace(match.group(2), '').strip('\n\r')
                level = indent_str.count('│   ') + indent_str.count('├──') + indent_str.count('└──')
                name = match.group(2).strip()
                is_directory = not '.' in name and not name.lower().endswith(('.md', '.txt', '.json', '.py', '.csv'))
                if name:
                    structure.append({
                        "name": name,
                        "level": level,
                        "is_directory": is_directory,
                        "raw_line": line.strip()
                    })
    except FileNotFoundError:
        st.error(f"❌ Fichier introuvable : '{file_path}'")
    except Exception as e:
        st.error(f"⚠️ Erreur de parsing : {e}")
    return structure

# --- Fonction cockpitifiée pour navigation ---
def display_structure(structure):
    if not structure:
        st.info("Structure vide ou invalide.")
        return

    if 'current_structure_path' not in st.session_state:
        st.session_state.current_structure_path = []

    current_level = len(st.session_state.current_structure_path)
    path_display = " / ".join(st.session_state.current_structure_path)
    st.markdown(f"**📂 Chemin courant :** `/ {path_display}` (niveau {current_level})")

    if current_level > 0:
        if st.button("⬅️ Remonter d’un niveau"):
            st.session_state.current_structure_path.pop()
            st.experimental_rerun()

    # Recherche du point d’entrée
    parent_index = -1
    if current_level > 0:
        for i, item in enumerate(structure):
            if item['name'] == st.session_state.current_structure_path[-1] and item['level'] == current_level - 1:
                parent_index = i
                break

    # Filtrage des enfants directs
    filtered_structure = []
    if parent_index != -1:
        for i in range(parent_index + 1, len(structure)):
            item = structure[i]
            if item['level'] == current_level:
                filtered_structure.append(item)
            elif item['level'] < current_level:
                break
    else:
        filtered_structure = [item for item in structure if item['level'] == 0]

    # 🔍 Filtre cockpitifié
    search_query = st.text_input("🔎 Filtrer par nom", "")
    if search_query:
        filtered_structure = [item for item in filtered_structure if search_query.lower() in item['name'].lower()]

    # Affichage cockpitifié des éléments
    for item in filtered_structure:
        if item['is_directory']:
            if st.button(f"📁 {item['name']}", key=f"dir_{item['name']}_{item['level']}"):
                st.session_state.current_structure_path.append(item['name'])
                st.experimental_rerun()
        else:
            st.markdown(f"📝 `{item['name']}`")

# --- Interface utilisateur ---
st.sidebar.header("📂 Source de la Structure")
structure_file_path = st.sidebar.text_input("Chemin vers `oliPLUS_structure.txt`", value="oliPLUS_structure.txt")

# Chargement
structure = load_and_parse_structure(structure_file_path)

if structure:
    with st.expander("📊 Aperçu cockpitifié"):
        total = len(structure)
        dirs = sum(1 for s in structure if s["is_directory"])
        files = total - dirs
        st.metric("Total éléments", total)
        st.metric("Dossiers", dirs)
        st.metric("Fichiers", files)

    st.markdown("---")
    display_structure(structure)

st.sidebar.markdown("---")
st.sidebar.info("Ce tableau cockpit vous permet de naviguer dans la structure typée du projet OliPLUS.")
