import streamlit as st
import json
import subprocess
from pathlib import Path
from migrate import migrate

# 🛠️ Configuration de la page
st.set_page_config(page_title="Migration vers cockpit OliPLUS", page_icon="📦")
st.title("📦 Migration vers Cockpit OliPLUS")

st.markdown("""
Ce module convertit des fichiers source en un **payload cockpitifié OliPLUS** prêt à afficher.  
Il peut aussi générer les fichiers complémentaires pour le moteur de dashboard 🚀
""")

# 📂 Paramètres utilisateur
docs_file = st.text_input("📄 Fichier de documents source", value="oliplus_docs.json")
meta_file = st.text_input("📑 Fichier de métadonnées (optionnel)", value="oliplus_metadata.json")
output_dir = st.text_input("📁 Répertoire d’export", value="payloads/")
dry_run = st.checkbox("🔬 Simulation seulement (dry-run)", value=False)
generate_cockpit_files = st.checkbox("📂 Générer automatiquement `cockpit_files.json`", value=True)

# 🚀 Lancement de la migration
if st.button("Lancer la migration 🛠️"):
    with st.spinner("⏳ Traitement en cours..."):

        # ⚙️ Étape 1 : génération cockpit_files.json
        if generate_cockpit_files:
            st.markdown("#### ⚙️ Génération des fichiers cockpit...")
            try:
                subprocess.run(["python", "generate_cockpit_files_section.py"], check=True)
                st.success("📂 `cockpit_files.json` généré avec succès.")
            except subprocess.CalledProcessError as e:
                st.error(f"🚫 Échec de génération `cockpit_files.json` : {e}")
            except Exception as e:
                st.warning(f"⚠️ Erreur inattendue : {e}")

        # ⚙️ Étape 2 : exécution de la migration
        st.markdown("#### ⚙️ Exécution de la migration...")
        try:
            result = migrate(
                classification_path="classification_structure.yaml",
                docs_path=docs_file,
                meta_path=meta_file,
                output_dir=output_dir,
                dry_run=dry_run
            )

            # ✅ Résultat
            if dry_run:
                st.info("🧪 Simulation terminée — aucun fichier exporté.")
            else:
                st.success("✅ Migration cockpit complétée avec succès.")

            # 🧾 Résumé des opérations
            st.markdown("### 🧾 Résumé")
            st.markdown(f"""
            • **{result.get('docs', 0)}** documents traités  
            • **{result.get('metadata', 0)}** métadonnées associées  
            • **{len(result.get('doc_types', []) or [])}** types reconnus  
            • **{len(result.get('export_data', {}).get('cockpit_files', []))}** fichiers cockpit injectés
            """)

            # 🧩 Aperçu du payload
            export_data = result.get("export_data", {})
            todo_preview = export_data.get("todo_inventory", [])
            if todo_preview:
                st.markdown("### 🧩 Extrait du payload (`todo_inventory`)")
                st.json(todo_preview[:5])
            else:
                st.warning("⚠️ Aucun contenu disponible pour prévisualisation.")

            # 📥 Téléchargement du fichier exporté
            output_path = result.get("output_path")
            if not dry_run and output_path and Path(output_path).exists():
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="📥 Télécharger le payload exporté",
                        data=f,
                        file_name=Path(output_path).name,
                        mime="application/json"
                    )
                st.code(f"🕒 Fichier exporté : {Path(output_path).name}")
            elif not dry_run:
                st.warning("⚠️ Fichier exporté introuvable.")

        except Exception as e:
            st.error(f"🚫 Erreur pendant la migration : {e}")
