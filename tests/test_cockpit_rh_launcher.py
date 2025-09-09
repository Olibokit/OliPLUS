import logging
import json
from datetime import datetime
import streamlit as st
from pathlib import Path

from upload_documents import launch_ocr
from export_metrics import run_metrics_export
from dashboard_ui import start_dashboard
from cockpit_search import start_search
from simulate_capture import simulate_rh_capture
from verify_provenance import audit_documents
from approval_chain import approval_chain

# 🪵 Logger cockpit
LOG_FORMAT = "%(asctime)s — %(levelname)s — 📘 %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("cockpit")

# 📁 Fichier d’export JSON
STATUS_FILE = Path("cockpit_status.json")

# 🔧 Modules à lancer
MODULES = {
    "OCR des documents": launch_ocr,
    "Export des métriques": run_metrics_export,
    "Dashboard UI": start_dashboard,
    "Recherche cockpit": start_search,
    "Capture RH simulée": simulate_rh_capture,
    "Audit de provenance": audit_documents
}

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_launch(name: str, func):
    try:
        logger.info(f"🔹 Lancement : {name}")
        func()
        return {"status": "success", "timestamp": timestamp()}
    except Exception as e:
        logger.warning(f"⚠️ Échec {name} : {e}")
        return {"status": "error", "timestamp": timestamp(), "error": str(e)}

def run_all_modules():
    logger.info("📘 Démarrage cockpit RH & édition...")
    results = {name: safe_launch(name, func) for name, func in MODULES.items()}

    # 🔐 Validation cockpit RH
    logger.info("🔐 Chaîne d'approbation RH :")
    for level in approval_chain.get("levels", []):
        status = "✅" if level.get("canApprove") else "⛔"
        logger.info(f" • {level.get('role')} → {status} validation cockpit")

    # 📊 Résumé final
    logger.info("📊 Résumé du lancement cockpit :")
    for name, result in results.items():
        icon = "✅" if result["status"] == "success" else "❌"
        logger.info(f"{icon} {name} — {result['timestamp']}")

    # 💾 Export JSON
    try:
        STATUS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
        logger.info(f"📝 Statut exporté dans {STATUS_FILE}")
    except Exception as e:
        logger.error(f"Erreur d’export JSON : {e}")

    return results

# 🖥️ Interface Streamlit
def cockpit_ui():
    st.set_page_config(page_title="Cockpit RH", page_icon="🛫", layout="wide")
    st.title("🛫 Cockpit RH — Lancement des modules")
    st.markdown("Lancez chaque module individuellement ou tous en une seule fois.")

    if st.button("🚀 Lancer tous les modules"):
        with st.spinner("Lancement en cours..."):
            results = run_all_modules()
        st.success("Lancement complet terminé.")
        st.json(results)

    st.subheader("📦 Modules individuels")
    for name, func in MODULES.items():
        if st.button(f"▶️ {name}"):
            with st.spinner(f"Lancement de {name}..."):
                result = safe_launch(name, func)
            if result["status"] == "success":
                st.success(f"{name} lancé avec succès à {result['timestamp']}")
            else:
                st.error(f"{name} a échoué : {result['error']}")

    st.subheader("🔐 Chaîne d'approbation RH")
    for level in approval_chain.get("levels", []):
        status = "✅" if level.get("canApprove") else "⛔"
        st.write(f" • {level.get('role')} → {status} validation cockpit")

if __name__ == "__main__":
    try:
        import streamlit.web.bootstrap
        cockpit_ui()
    except ImportError:
        logger.warning("Streamlit non disponible — lancement en mode console.")
        run_all_modules()
