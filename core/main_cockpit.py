import streamlit as st
from pathlib import Path
import json
from sync_engine import SyncEngine
from main_dashboard import launch_dashboard
from datetime import datetime

# 📁 Définir le chemin de configuration
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "json" / "config.json"

# 🔧 Chargement de la configuration
def load_config(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Erreur de chargement de la configuration : {e}")
        st.stop()

config = load_config(CONFIG_PATH)
PROJECT_ROOT = Path(config.get("rootDir", BASE_DIR))

# 🔄 Initialisation du moteur de synchronisation
def init_sync_engine(root, config_path):
    try:
        st.info("🔄 Synchronisation des modules...")
        sync = SyncEngine(root, config_path)
        sync.run_scan()
        sync.build_graph()
        st.success(f"✅ Modules synchronisés ({datetime.now().strftime('%d/%m/%Y %H:%M:%S')})")
        return sync
    except Exception as e:
        st.warning(f"⚠️ Problème de synchronisation : {e}")
        st.stop()

sync = init_sync_engine(PROJECT_ROOT, CONFIG_PATH)

st.title("🧩 Rapport de synchronisation cockpit")

# 📊 Résumé global
with st.expander("📊 Résumé global"):
    st.metric("📁 Fichiers scannés", sync.total_files)
    st.metric("⚠️ Problèmes détectés", sync.total_issues)
    st.metric("✅ Modules valides", sync.total_valid)

# 📥 Export du rapport
if st.button("📥 Exporter le rapport"):
    report = sync.generate_report()  # Assure-toi que cette méthode existe
    st.download_button("Télécharger", report.encode("utf-8"), file_name="rapport_sync.txt")

# 🧭 Vues détaillées
def show_missing_scripts():
    missing = sync.check_dashboard_scripts()
    if missing:
        st.subheader("📁 Scripts manquants")
        for name, path in missing:
            st.error(f"❌ {name} → `{path}` introuvable")
    else:
        st.success("✅ Tous les scripts du dashboard sont présents.")

def show_extension_mismatches():
    mismatch = sync.check_extension_mismatch()
    if mismatch:
        st.subheader("🧩 Extensions désactivées mais présentes")
        for ext in mismatch:
            st.warning(f"⚠️ Extension `{ext}` présente physiquement mais désactivée dans la config.")
    else:
        st.success("✅ Cohérence entre extensions activées et fichiers présents.")

def show_dependency_issues():
    issues = sync.check_python_dependencies()
    if issues:
        st.subheader("📦 Problèmes de dépendances")
        for pkg, installed, required in issues:
            st.warning(f"⚠️ {pkg} : installé `{installed}`, requis `{required}`")
    else:
        st.success("✅ Toutes les dépendances sont conformes.")

def show_missing_links():
    missing = sync.resolve_missing_links()
    if missing:
        st.subheader("🔗 Modules référencés mais absents")
        for m in missing:
            st.error(f"❌ Fichier manquant : `{m}`")
    else:
        st.success("✅ Aucun module référencé manquant.")

def show_dependency_graph():
    st.subheader("📈 Graphe de dépendances")
    st.graphviz_chart(sync.visualize_graph())

# 🧭 Exécution des vues
show_missing_scripts()
show_extension_mismatches()
show_dependency_issues()
show_missing_links()
show_dependency_graph()

# 🚀 Lancement du dashboard cockpit
st.divider()
st.button("🧭 Lancer le cockpit", on_click=launch_dashboard)
