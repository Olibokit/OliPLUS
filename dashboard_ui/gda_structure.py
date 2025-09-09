import streamlit as st
from gda_tools import deploy_gda_structure

def render():
    st.set_page_config(
        page_title="Structure GDA",
        page_icon="📁",
        layout="centered"
    )
    st.title("📁 Génération automatique de la structure documentaire GDA")

    st.markdown(
        """
        Ce module permet de créer ou synchroniser la structure documentaire **GDA** 📚  
        ➤ Utile lors du démarrage d’un projet ou pour synchroniser les répertoires avec le cockpit.

        👉 Les dossiers nécessaires seront créés automatiquement dans les emplacements configurés.
        """
    )

    if st.button("🛠️ Créer ou actualiser les dossiers GDA"):
        with st.spinner("🧱 Création des dossiers en cours..."):
            try:
                created = deploy_gda_structure()
            except Exception as e:
                st.error(f"🚨 Une erreur est survenue : {e}")
                return

        if created:
            st.success(f"✅ {len(created)} dossier(s) généré(s) avec succès :")
            st.code("\n".join(created), language="bash")
        else:
            st.info("📂 Tous les dossiers GDA sont déjà présents. Aucune modification nécessaire.")

if __name__ == "__main__":
    render()
