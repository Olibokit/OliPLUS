import streamlit as st
import sys
from pathlib import Path

racine = Path(__file__).resolve().parent.parent
sys.path.append(str(racine))

try:
    from deploy_classification import deploy_classification_files
except ModuleNotFoundError:
    st.error("❌ Fichier 'deploy_classification.py' introuvable.")
    st.stop()

import requests  # Pour le webhook

def render():
    st.set_page_config(page_title="Déploiement Classification", page_icon="📦")
    st.title("📤 Déploiement des fichiers de classification")

    # === 🔍 Chargement dynamique des environnements
    def get_available_envs():
        # Tu peux remplacer ça par une lecture de fichier JSON ou une API
        return ["dev", "stage", "prod", "recette", "intégration"]

    envs = get_available_envs()
    env = st.selectbox("🌐 Choisir l’environnement cible", envs)

    # === 🧪 Option dry-run
    dry_run = st.checkbox("🧪 Simuler le déploiement (dry-run)", value=False)

    # === 🔔 Webhook dynamique
    use_webhook = st.checkbox("🔔 Activer l’envoi d’une alerte webhook", value=False)
    webhook_url = st.text_input("📡 URL du webhook (si activé)", placeholder="https://...")

    # === 📁 Affichage conditionnel selon l’environnement
    if env == "prod":
        st.warning("⚠️ Vous êtes sur l’environnement **production**. Soyez prudent.")
    elif env == "recette":
        st.info("🧪 Environnement de recette — idéal pour les tests fonctionnels.")
    else:
        st.info(f"🔧 Environnement sélectionné : {env}")

    # === 🚀 Action de déploiement
    if st.button("🚀 Lancer le déploiement maintenant"):
        with st.spinner("Déploiement en cours..."):
            try:
                log_output = deploy_classification_files(env=env, dry_run=dry_run)
                st.success(f"✅ Déploiement {'simulé' if dry_run else 'réel'} terminé ({env}).")
                st.code(log_output, language="text")
            except Exception as e:
                st.error(f"❌ Échec du déploiement : {e}")
                return

            # === 📡 Envoi du webhook si activé
            if use_webhook and webhook_url.startswith("http"):
                try:
                    payload = {
                        "status": "success",
                        "environment": env,
                        "dry_run": dry_run,
                        "log_excerpt": log_output[:500]
                    }
                    requests.post(webhook_url, json=payload)
                    st.info("📡 Webhook envoyé avec succès.")
                except Exception as e:
                    st.warning(f"⚠️ Échec du webhook : {e}")
            elif use_webhook:
                st.warning("⚠️ URL du webhook invalide.")

    # === 📜 Logs cockpit avec filtre dynamique
    log_path = racine / "6000_INFORMATION_ET_COMMUNICATIONS" / "1100_GOUVERNANCE_INFORMATION" / ".copilot_classification.log"
    st.subheader("🧾 Derniers logs cockpit")

    if log_path.exists():
        search_term = st.text_input("🔍 Filtrer les logs par mot-clé")
        with st.expander("📂 Voir les logs détaillés"):
            try:
                logs = log_path.read_text(encoding="utf-8")
                if search_term:
                    logs = "\n".join([line for line in logs.splitlines() if search_term.lower() in line.lower()])
                st.text(logs)
            except Exception as e:
                st.warning(f"⚠️ Impossible de lire le fichier de log : {e}")
    else:
        st.info("ℹ️ Aucun log trouvé pour le moment.")

