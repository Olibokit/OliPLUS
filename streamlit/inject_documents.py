import streamlit as st
import pandas as pd
import os
import uuid
import json
import yaml
from datetime import datetime, timezone
from io import StringIO

# === Configuration cockpitifiée ===
TEEDY_API_BASE_URL = os.getenv("TEEDY_API_URL", "http://localhost:80/api")
TEEDY_API_KEY = os.getenv("TEEDY_API_KEY", "your_teedy_api_key_here")
DOCUMENTS_MANIFEST_PATH = "documents_manifest.yaml"

# === Fonction simulée : injection typée ===
def simulate_document_injection(file_name, collection_id, source_app, user_id, metadata=None):
    st.info(f"📤 Simulation de l'envoi de `{file_name}` vers la collection `{collection_id}`...")
    document_id = f"teedy-doc-{uuid.uuid4().hex[:8]}"
    checksum = uuid.uuid4().hex
    size_bytes = len(file_name.encode("utf-8")) * 1000
    artefact_info = {
        "document_id": document_id,
        "original_filename": file_name,
        "target_collection": collection_id,
        "mime_type": "application/octet-stream",
        "size_bytes": size_bytes,
        "checksum_sha256": checksum,
        "status_individual": "success"
    }
    return artefact_info

# === Fonction simulée : ajout au manifeste cockpitifié ===
def append_to_documents_manifest(uuid_upload, source_app, user_id_injector, artefacts, status="success", error_details=None):
    manifest_entry = {
        "uuid_upload": str(uuid_upload),
        "source_app": source_app,
        "timestamp_injection": datetime.now(timezone.utc).isoformat(timespec='seconds'),
        "user_id_injector": user_id_injector,
        "status": status,
        "artefacts": artefacts
    }
    if error_details:
        manifest_entry["error_details"] = error_details

    st.markdown("### 🧾 Entrée du manifeste cockpit (simulation)")
    st.json(manifest_entry)
    st.success("✅ Opération d'injection cockpit simulée et enregistrée.")
    return manifest_entry

# === Interface Streamlit cockpitifiée ===
st.set_page_config(page_title="📤 Upload Documentaire Cockpit", layout="wide")
st.title("📤 Injection & Traçabilité Documentaire Cockpit")

st.markdown("Simulez l'injection typée de documents dans le système Cockpit et visualisez leur traçabilité.")

# === Formulaire cockpit d'injection ===
st.header("🆕 Injecter un nouveau document")

manifests = []

with st.form("upload_form"):
    uploaded_file = st.file_uploader("📂 Sélectionnez un document à injecter", type=["pdf", "docx", "txt", "jpg", "png"])
    collection_id = st.text_input("🗂️ ID de la collection cible", value="default_collection")
    source_app_name = st.text_input("🖥️ Nom de l'application source", value="ManuelUpload")
    user_id_input = st.text_input("👤 ID de l'utilisateur injecteur", value="demo_user")
    metadata_input = st.text_area("🧾 Métadonnées JSON (optionnel)", value='{"tags": ["demo"]}')

    submitted = st.form_submit_button("🚀 Injecter le document")

    if submitted:
        if uploaded_file is not None:
            st.write(f"📁 Fichier sélectionné : `{uploaded_file.name}`")
            try:
                metadata = json.loads(metadata_input)
            except json.JSONDecodeError:
                st.error("❌ Format JSON des métadonnées invalide.")
                metadata = {}

            operation_uuid = uuid.uuid4()
            artefact = simulate_document_injection(
                uploaded_file.name,
                collection_id,
                source_app_name,
                user_id_input,
                metadata
            )
            if artefact:
                manifest = append_to_documents_manifest(operation_uuid, source_app_name, user_id_input, [artefact])
                manifests.append(manifest)
                st.success(f"✅ Document `{uploaded_file.name}` injecté (simulation).")
            else:
                st.error(f"❌ Échec de l'injection simulée pour `{uploaded_file.name}`.")
        else:
            st.warning("⚠️ Veuillez sélectionner un fichier à injecter.")

# === Section cockpit : historique simulé des injections ===
st.header("📜 Historique des Injections (simulation cockpit)")

sample_data = [
    {"uuid_upload": "abc-123", "source_app": "Archivesspace", "timestamp": "2025-07-18T14:00:00Z", "status": "success", "files": 2},
    {"uuid_upload": "def-456", "source_app": "TeedyCLI", "timestamp": "2025-07-17T09:30:00Z", "status": "partial_failure", "files": 1},
    {"uuid_upload": "ghi-789", "source_app": "ManuelUpload", "timestamp": "2025-07-16T16:45:00Z", "status": "success", "files": 3},
]
df_history = pd.DataFrame(sample_data)

if manifests:
    for m in manifests:
        df_history.loc[len(df_history)] = {
            "uuid_upload": m["uuid_upload"],
            "source_app": m["source_app"],
            "timestamp": m["timestamp_injection"],
            "status": m["status"],
            "files": len(m["artefacts"])
        }

if not df_history.empty:
    st.dataframe(df_history, use_container_width=True, hide_index=True)
else:
    st.info("📭 Aucun historique d'injection cockpit à afficher.")

# === Export cockpit typé ===
st.header("📤 Export cockpit")

col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Exporter en CSV"):
        csv = df_history.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger le CSV", data=csv, file_name="historique_injections.csv", mime="text/csv")

with col2:
    if st.button("📥 Exporter en YAML"):
        yaml_data = yaml.dump(manifests, sort_keys=False, allow_unicode=True)
        st.download_button("Télécharger le YAML", data=yaml_data, file_name="manifeste_injections.yaml", mime="text/yaml")
