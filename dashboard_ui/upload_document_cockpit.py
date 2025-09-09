import streamlit as st
import requests

def render():
    st.title("📤 Upload de document cockpit")
    st.markdown("Remplis les métadonnées et sélectionne un fichier PDF à envoyer au backend.")

    with st.form("upload_form"):
        user = st.text_input("👤 Utilisateur")
        title = st.text_input("📘 Titre du document")
        author = st.text_input("✍️ Auteur")
        source = st.text_input("📡 Source")
        statut = st.selectbox("📌 Statut cockpit", ["Numérisé", "En attente droits", "Rejeté"])
        doc_type = st.selectbox("📂 Type de document", ["Poésie", "Fiche RH", "Contrat", "Autre"])
        file = st.file_uploader("📄 Fichier PDF", type=["pdf"])
        submitted = st.form_submit_button("🚀 Envoyer")

    if submitted:
        if not file:
            st.warning("📎 Aucun fichier sélectionné.")
            return

        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        data = {
            "user": user.strip(),
            "title": title.strip(),
            "author": author.strip(),
            "source": source.strip(),
            "statut_cockpit": statut,
            "document_type": doc_type
        }

        try:
            res = requests.post("http://localhost:8000/upload-pdf", data=data, files=files)
            if res.ok:
                st.success(res.json().get("message", "✅ Document envoyé avec succès."))
            else:
                st.error(f"❌ Erreur : {res.json().get('detail', 'Réponse inattendue du serveur.')}")
        except requests.exceptions.ConnectionError:
            st.error("🚫 Connexion au backend impossible.")
        except Exception as e:
            st.error(f"⚠️ Erreur inattendue : {e}")
