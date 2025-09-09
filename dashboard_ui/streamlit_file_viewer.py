import streamlit as st
import os

BASE_DIR = os.path.dirname(__file__)
SUPPORTED_EXTENSIONS = [".py", ".yaml", ".yml", ".ps1", ".html", ".css", ".json", ".sql"]

def scan_files(root, extensions):
    found = []
    for folder, _, files in os.walk(root):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in extensions:
                found.append(os.path.join(folder, f))
    return found

def display_file(path):
    ext = os.path.splitext(path)[1].lower()
    st.subheader(f"📄 Fichier : `{os.path.basename(path)}`")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if ext == ".py":
            st.code(content, language="python")
        elif ext in [".yaml", ".yml"]:
            st.code(content, language="yaml")
        elif ext == ".ps1":
            st.code(content, language="powershell")
        elif ext == ".html":
            st.code(content, language="html")
        elif ext == ".css":
            st.code(content, language="css")
        elif ext == ".json":
            st.json(content)
        elif ext == ".sql":
            st.code(content, language="sql")
        else:
            st.text(content)
    except Exception as e:
        st.error(f"Erreur lors de la lecture : {e}")

st.set_page_config(page_title="Cockpit OiiPLUS", layout="wide")
st.sidebar.title("🧭 Fichiers disponibles")

files = scan_files(BASE_DIR, SUPPORTED_EXTENSIONS)
selected = st.sidebar.selectbox("Choisissez un fichier :", files)

if selected:
    display_file(selected)
