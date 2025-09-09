import streamlit as st
import os
import subprocess
import webbrowser
import urllib.request

st.set_page_config(page_title="Cockpit OliPLUS", layout="centered")

st.title("🧭 Cockpit OliPLUS")
st.markdown("Interface de contrôle et de diagnostic du système.")

# === État du système ===
st.subheader("🔍 État du système")

def check(command):
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True, check=True)
        return True
    except Exception:
        return False

status = {
    "🐍 Python": check("python --version"),
    "📦 Streamlit": check("python -m streamlit --version"),
    "🐳 Docker": check("docker --version"),
    "🕸️ Django": check("python -m django --version")
}

for name, ok in status.items():
    st.markdown(f"- {name} : {'✅ OK' if ok else '❌ MANQUANT'}")

# === Rapport HTML ===
st.subheader("📄 Rapport système")

report_path = os.path.join(os.environ["USERPROFILE"], "OliPLUS", "logs", "system_report.html")

if os.path.exists(report_path):
    if st.button("🧾 Ouvrir le rapport HTML"):
        try:
            webbrowser.open(report_path)
            st.success("Rapport ouvert dans le navigateur.")
        except Exception as e:
            st.error(f"Erreur lors de l'ouverture du rapport : {e}")
else:
    st.warning(f"⚠️ Rapport non trouvé : {report_path}")

# === Vérification de version ===
st.subheader("🔄 Vérification de version OliPLUS")

local_version = "1.2.0"
version_url = "https://oliplus.com/version.txt"

try:
    response = urllib.request.urlopen(version_url, timeout=5)
    remote_version = response.read().decode().strip()
    if remote_version != local_version:
        st.error(f"🆕 Mise à jour disponible : version {remote_version}")
    else:
        st.success("✅ Version OliPLUS à jour.")
except Exception as e:
    st.warning(f"⚠️ Impossible de vérifier la version distante : {e}")

# === Relancer le launcher ===
st.subheader("🚀 Relancer le launcher OliPLUS")

bat_path = os.path.join(os.environ["USERPROFILE"], "OliPLUS", "dashboard", "main", "OliPLUS_launcher.bat")

if os.path.exists(bat_path):
    if st.button("▶️ Lancer OliPLUS.bat"):
        try:
            subprocess.Popen(["cmd", "/c", bat_path], shell=True)
            st.success("Launcher relancé avec succès.")
        except Exception as e:
            st.error(f"❌ Erreur lors du lancement : {e}")
else:
    st.error(f"❌ Fichier introuvable : {bat_path}")
