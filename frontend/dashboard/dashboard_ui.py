import streamlit as st
import os, json, datetime, subprocess, requests, importlib.util
from pathlib import Path
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh

# 🔄 Actualisation automatique toutes les 30 secondes
st_autorefresh(interval=30_000, key="refresh")

# ⚙️ Configuration de la page
st.set_page_config(page_title="Cockpit OPILUS", page_icon="🧭", layout="wide")
st.title("🧭 Cockpit central OPILUS")
st.markdown("---")

# 📁 Chargement de la configuration
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "json" / "config.json"

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    st.error(f"❌ Erreur de chargement de la configuration : {e}")
    st.stop()

PROJECT_ROOT = Path(config.get("rootDir", BASE_DIR))
SUPPORTED_EXTENSIONS = [".py", ".json", ".yaml", ".yml", ".html", ".css", ".ps1", ".sql", ".md", ".txt", ".log"]

# 🔧 Fonctions utilitaires
def get_last_update(path: Path) -> str:
    try:
        return datetime.datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return "Jamais"

def safe_run(script_path: str, label: str) -> None:
    full_path = PROJECT_ROOT / script_path
    if full_path.exists():
        subprocess.Popen(["streamlit", "run", str(full_path)])
        st.success(f"{label} lancé.")
    else:
        st.error(f"{label} introuvable : {full_path}")

def send_slack_alert(message: str) -> None:
    webhook_url = config.get("notifications", {}).get("slackWebhook", "")
    if webhook_url:
        try:
            requests.post(webhook_url, json={"text": message})
        except Exception:
            st.warning("⚠️ Échec d'envoi vers Slack.")

def scan_project(root_dir: Path) -> dict:
    structure = {}
    for file_path in root_dir.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower() or "no_extension"
            if ext in SUPPORTED_EXTENSIONS:
                structure.setdefault(ext, []).append(file_path)
    return structure

# 🧩 Vues cockpit
def render_overview() -> None:
    st.header("📋 Vue d'ensemble du projet")
    structure = scan_project(PROJECT_ROOT)
    for ext, files in structure.items():
        st.subheader(f"Fichiers {ext.upper().replace('.', '')}")
        with st.expander("Afficher/Masquer"):
            for file_path in files:
                st.markdown(f"**`{file_path.relative_to(PROJECT_ROOT)}`**")
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if "Gemini" in content:
                        st.info("🧠 Module Gemini détecté.")
                        if st.button(f"Lancer Gemini ({file_path.name})"):
                            st.success("Lancement simulé du module Gemini.")
                    if ext == ".md":
                        st.markdown(content)
                    elif ext == ".json":
                        st.json(json.loads(content))
                    elif ext in [".log", ".txt", ".py", ".sql", ".ps1"]:
                        st.code(content, language=ext[1:])
                    else:
                        st.text(content)
                except Exception as e:
                    st.error(f"Erreur d'affichage : {e}")
                st.markdown("---")

def render_modules() -> None:
    st.header("🧩 Modules détectés")
    modules_path = PROJECT_ROOT / "modules"
    if not modules_path.exists():
        st.info("Aucun module détecté.")
        return
    for module_dir in modules_path.iterdir():
        if module_dir.is_dir():
            st.subheader(f"⚙️ Module : {module_dir.name}")
            st.text("Statut : ✅ Actif")
            if module_dir.name == "ia_synopsis":
                st.success("Intégration Gemini disponible.")
                if st.button("Démonstration IA"):
                    st.write("Lancement de la génération de synopsis...")
            st.markdown("---")

def render_stats() -> None:
    st.header("📈 Statistiques système")
    sys = {"cpu": 60, "memory": 70}
    col1, col2, col3 = st.columns(3)
    col1.metric("🧠 CPU (%)", f"{sys['cpu']}%", f"{sys['cpu'] - 50}%")
    col2.metric("💾 Mémoire (%)", f"{sys['memory']}%", f"{sys['memory'] - 60}%")
    col3.metric("👥 Utilisateurs actifs", 12)

    data = pd.DataFrame({
        "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=20, freq="T"),
        "CPU": [60 + i % 10 for i in range(20)],
        "Mémoire": [70 + i % 5 for i in range(20)],
    })

    for metric, color in [("CPU", "orange"), ("Mémoire", "purple")]:
        st.altair_chart(
            alt.Chart(data).mark_line(color=color).encode(
                x="timestamp:T", y=f"{metric}:Q", tooltip=["timestamp", metric]
            ).properties(title=f"Utilisation {metric} (%)"),
            use_container_width=True
        )

def render_alertes() -> None:
    st.header("🔔 Logs & Alertes")
    alerts = []
    logs_path = Path(config.get("logging", {}).get("logFilePath", PROJECT_ROOT / "logs" / "error.log"))
    try:
        with open(logs_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[-50:]:
                if any(level in line for level in ["ERROR", "CRITICAL", "ERREUR"]):
                    alerts.append(line.strip())
    except FileNotFoundError:
        alerts.append("⚠️ Aucun fichier de log trouvé.")

    if alerts:
        for alert in alerts:
            st.error(alert)
            if config.get("notifications", {}).get("enableToast"):
                send_slack_alert(f"🚨 Alerte système : {alert}")
    else:
        st.success("✅ Aucun problème détecté.")

def render_actions() -> None:
    st.header("⚙️ Actions rapides")
    col1, col2, col3 = st.columns(3)
    if col1.button("🔁 Recharger GDA"):
        safe_run("gda/gda_render.py", "GDA")
    if col2.button("📚 Ouvrir Cockpit"):
        safe_run("dashboard/cockpit_documents_and_stats.py", "Cockpit")
    if col3.button("📂 Voir les logs"):
        logs_folder = os.path.dirname(str(config.get("logging", {}).get("logFilePath", "")))
        st.markdown(f"[📁 Ouvrir les logs]({logs_folder})")

def render_config() -> None:
    st.header("⚙️ Configuration")
    st.json(config)

def render_extensions() -> None:
    st.header("🧩 Extensions activées")
    ext_root = PROJECT_ROOT / config["extensions"].get("scanFolder", "extensions")
    extensions = [ext for ext, enabled in config["extensions"]["enabled"].items() if enabled]
    for ext in extensions:
        try:
            module_path = ext_root / ext / "render.py"
            spec = importlib.util.spec_from_file_location(ext, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.render()
        except Exception as e:
            st.warning(f"Extension {ext} non chargée : {e}")

# 📂 Navigation cockpit
st.sidebar.title("📂 Navigation cockpit")
mode = config.get("activeMode", "Utilisateur")
st.sidebar.markdown(f"**Mode actif : `{mode}`**")

page = st.sidebar.radio("Choisir une vue :", [
    "📋 Vue d'ensemble du projet", "🧩 Modules détectés", "📈 Statistiques système",
    "🔔 Logs & Alertes", "⚙️ Actions rapides", "⚙️ Configuration", "🧩 Extensions activées"
])

routes = {
    "📋 Vue d'ensemble du projet": render_overview,
    "🧩 Modules détectés": render_modules,
    "📈 Statistiques système": render_stats,
    "🔔 Logs & Alertes": render_alertes,
    "⚙️ Actions rapides": render_actions,
    "⚙️ Configuration": render_config,
    "🧩 Extensions activées": render_extensions
}

routes.get(page, lambda: st.error("❌ Vue inconnue."))()
