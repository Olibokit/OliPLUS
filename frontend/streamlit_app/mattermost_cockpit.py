import streamlit as st
import requests
from datetime import datetime

# 📌 Prérequis cockpit :
# Ce script suppose que l’API Mattermost est accessible via http://localhost:8065/api/v4
# et qu’un token utilisateur ou admin est disponible pour l’authentification.

# 🏷️ Configuration de la page
st.set_page_config(page_title="Cockpit Mattermost RH", page_icon="💬")
st.title("💬 Cockpit Mattermost RH")

# 📄 Description cockpitifiée
st.markdown("""
Bienvenue dans l'interface cockpitifiée pour accéder à Mattermost RH.  
Utilisée pour les échanges internes, audits, et coordination RH confidentielle.
""")

# ⚠️ Affichage du prérequis dans l'interface
st.warning("""
📌 Ce cockpit nécessite :
- Un serveur Mattermost actif sur `localhost:8065`
- L’API REST exposée sur `/api/v4`
- Un token d’accès valide (utilisateur ou admin)
""")

# 🔐 Authentification cockpitifiée
st.subheader("🔐 Authentification")
token = st.text_input("🔑 Token d'accès Mattermost", type="password")

mattermost_url = "http://localhost:8065"
api_url = f"{mattermost_url}/api/v4"

headers = {"Authorization": f"Bearer {token}"} if token else {}

# ✅ Vérification du serveur et du token
if token:
    try:
        me = requests.get(f"{api_url}/users/me", headers=headers, timeout=3)
        if me.status_code == 200:
            user = me.json()
            st.success(f"✅ Connecté en tant que : {user['username']}")
        else:
            st.error("🚫 Token invalide ou expiré.")
    except requests.exceptions.RequestException:
        st.error("❌ Impossible de joindre le serveur Mattermost.")

# 📁 Vue des canaux RH
if token and st.checkbox("📂 Afficher les canaux RH"):
    try:
        channels = requests.get(f"{api_url}/users/me/channels", headers=headers).json()
        rh_channels = [c for c in channels if "rh" in c["name"].lower()]
        st.write("📋 Canaux RH détectés :")
        for c in rh_channels:
            st.markdown(f"- **{c['display_name']}** (`{c['name']}`)")
    except Exception as e:
        st.warning(f"⚠️ Erreur lors de la récupération des canaux : {e}")

# 📊 Dashboard RH cockpitifié
if token and st.checkbox("📊 Afficher les statistiques RH"):
    try:
        posts = requests.get(f"{api_url}/users/me/posts", headers=headers).json()
        total_posts = len(posts.get("order", []))
        st.metric("📨 Messages envoyés", total_posts)

        now = datetime.now()
        st.caption(f"📅 Statistiques générées le {now:%d/%m/%Y à %H:%M}")
    except Exception:
        st.warning("⚠️ Statistiques non disponibles pour ce compte.")

# 🧭 Accès direct
if st.button("🔗 Ouvrir Mattermost cockpit"):
    st.markdown(f"[➡️ Accéder à Mattermost]({mattermost_url})", unsafe_allow_html=True)

# 💡 Astuce cockpit
st.info("💡 Astuce : Vous pouvez intégrer Mattermost dans un iframe cockpit ou automatiser les notifications RH via webhook.")
