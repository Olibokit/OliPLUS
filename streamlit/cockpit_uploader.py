import streamlit as st
from upload_documents import upload_document, load_documents_db, DocumentUploadError

st.set_page_config(page_title="📘 Cockpit Uploader", layout="wide")

st.title("📘 Cockpit Document Uploader")
st.markdown("Interface typée pour injecter des documents dans la base cockpit JSON.")

with st.form("upload_form"):
    st.subheader("📤 Nouveau document cockpit")
    uploaded_file = st.file_uploader("Fichier à injecter", type=["pdf", "docx", "txt"])
    title = st.text_input("Titre du document")
    author = st.text_input("Auteur")
    document_type = st.selectbox("Type de document", ["rapport", "manuel", "note", "autre"])
    tags = st.text_input("Tags (séparés par des virgules)")
    summary = st.text_area("Résumé du contenu")
    statut = st.selectbox("Statut cockpit", ["en attente", "numérisé", "validé"])

    submitted = st.form_submit_button("🚀 Injecter dans Cockpit")

    if submitted:
        if uploaded_file:
            try:
                result = upload_document(
                    file_content=uploaded_file.read(),
                    filename=uploaded_file.name,
                    title=title,
                    author=author,
                    document_type=document_type,
                    tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
                    content_summary=summary,
                    statut_cockpit=statut
                )
                st.success(f"✅ Document injecté : {result['title']} (ID: {result['id']})")
            except DocumentUploadError as e:
                st.error(f"❌ Erreur : {e}")
        else:
            st.warning("⚠️ Aucun fichier sélectionné.")

st.divider()
st.subheader("📂 Base cockpit actuelle")

docs = load_documents_db()
if docs:
    for doc in docs:
        with st.expander(f"📄 {doc['title']} — {doc['status']}"):
            st.write(f"**ID**: {doc['id']}")
            st.write(f"**Auteur**: {doc['author']}")
            st.write(f"**Type**: {doc['type']}")
            st.write(f"**Tags**: {', '.join(doc['tags'])}")
            st.write(f"**Résumé**: {doc['content_summary']}")
            st.write(f"**Fichier**: `{doc['file_path']}`")
            st.write(f"**Date d’injection**: {doc['date_uploaded_local']}")
else:
    st.info("📭 Aucun document dans la base cockpit.")
