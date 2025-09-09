import streamlit as st
import pandas as pd
import yaml
from io import StringIO

# === Configuration typée de la page cockpit ===
st.set_page_config(
    page_title="📊 Cockpit Tracker View",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Tableau de Suivi Cockpit")
st.markdown("Grille cockpitifiée de gouvernance documentaire, technique et manifestes injectés.")

# === Fonction cockpit : affichage typé de bloc ===
def display_table_block(title: str, dataframe: pd.DataFrame):
    st.subheader(title)
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

# === Données cockpitifiées ===
df_readme = pd.DataFrame([
    {"Type": "README", "Nom": "README_TeedyImportInjector.md", "Rôle cockpit": "Injection documentaire automatisée", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_ArchivesspaceToCockpit.md", "Rôle cockpit": "Transposition Archivesspace multi-runtime", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_GoMattermostBuild.md", "Rôle cockpit": "Build Mattermost Go + sécurité XMLSec", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_RHWebApacheCockpit.md", "Rôle cockpit": "WebApp RH cockpitifiée", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_CockpitContainers.md", "Rôle cockpit": "Services Docker injectés", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_CockpitBuildTools.md", "Rôle cockpit": "Outils shell / build utils cockpitifiés", "État": "❓ À envisager"},
    {"Type": "README", "Nom": "README_PyprojectCockpit.md", "Rôle cockpit": "Groupes de dépendances typés", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_UploadDocuments.md", "Rôle cockpit": "Injection + traçabilité typée", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_ExceptionsCockpit.md", "Rôle cockpit": "Typologie des erreurs et exceptions cockpit", "État": "✅ Fait"},
    {"Type": "README", "Nom": "README_CLI_Oli.md", "Rôle cockpit": "Commandes de l’interface CLI cockpit", "État": "✅ Fait"},
])

df_manifest = pd.DataFrame([
    {"Type": "Manifest", "Nom": "fusion_manifest.yaml", "Rôle cockpit": "Ajouter Teedy, Archivesspace, etc.", "État": "⏳ À mettre à jour"},
    {"Type": "Manifest", "Nom": "docker_manifest.yaml", "Rôle cockpit": "Dockerfiles cockpitifiés", "État": "⏳ À compiler"},
    {"Type": "Manifest", "Nom": "manifest_teedy_injector.yaml", "Rôle cockpit": "Injection vers Teedy", "État": "❓ À vérifier"},
    {"Type": "Manifest", "Nom": "dashboard_docker_manifest.yaml", "Rôle cockpit": "UI + services liés", "État": "✅ Fait"},
    {"Type": "Manifest", "Nom": "requirements/docker_build.in", "Rôle cockpit": "Dépendances système / build", "État": "⏳ À enrichir"},
    {"Type": "Manifest", "Nom": "manifest_dependencies.yaml", "Rôle cockpit": "Cartographie typée des dépendances", "État": "✅ Fait"},
    {"Type": "Manifest", "Nom": "documents_manifest.yaml", "Rôle cockpit": "Traçabilité des artefacts injectés", "État": "✅ Fait"},
    {"Type": "Manifest", "Nom": "errors_manifest.yaml", "Rôle cockpit": "Typologie des erreurs cockpit", "État": "✅ Fait"},
    {"Type": "Manifest", "Nom": "oli_cli_manifest.yaml", "Rôle cockpit": "Commandes typées de la CLI", "État": "✅ Fait"},
    {"Type": "Manifest", "Nom": "cockpit_manifest_master.yaml", "Rôle cockpit": "Manifeste souverain complet cockpit", "État": "✅ Fait"},
])

df_components = pd.DataFrame([
    {"Type": "Composant", "Nom": "dashboard_docker_view.py", "Rôle cockpit": "Streamlit monitor Docker cockpit", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "docker-compose.yml", "Rôle cockpit": "Déploiement typé des services liés", "État": "⏳ À enrichir"},
    {"Type": "Composant", "Nom": "docker_scan_env.py", "Rôle cockpit": "Scan typé ENV / CMD / EXPOSE Docker", "État": "❓ À vérifier"},
    {"Type": "Composant", "Nom": "cli_teedy_injector.py", "Rôle cockpit": "Injection CLI vers Teedy cockpitifié", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "dependencies_view.py", "Rôle cockpit": "Streamlit — filtrage des dépendances cockpit", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "reset_email.html", "Rôle cockpit": "Email de réinitialisation JWT cockpit", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "auth_utils.py", "Rôle cockpit": "JWT typé cockpit pour réinitialisation / auth", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "upload_documents_view.py", "Rôle cockpit": "Streamlit — upload / traçabilité cockpitifiée", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "document_dashboard_view.py", "Rôle cockpit": "Streamlit — exploration typée des documents injectés", "État": "✅ Fait"},
    {"Type": "Composant", "Nom": "cockpit_tracker_view.py", "Rôle cockpit": "Cette interface visuelle de suivi cockpit", "État": "✅ Fait"},
])

df_optionals = pd.DataFrame([
    {"Type": "Optionnel", "Nom": "dashboard_services_overview.md", "Rôle cockpit": "Vue cockpit agrégée des blocs actifs", "État": "🚫 Non pertinent"},
    {"Type": "Optionnel", "Nom": "compose_runtime_overview.md", "Rôle cockpit": "Cartographie des runtime Docker cockpit", "État": "🚫 Non pertinent"},
    {"Type": "Optionnel", "Nom": "audit_docker_env.yaml", "Rôle cockpit": "ENV / CMD cockpitifiés extraits", "État": "🚫 Non pertinent"},
])

# === Affichage cockpitifié ===
display_table_block("✅ README à créer ou compléter", df_readme)
display_table_block("🗂️ Manifestes à injecter", df_manifest)
display_table_block("💻 Composants techniques / UI cockpit", df_components)
display_table_block("🧬 Optionnels cockpitifiés utiles", df_optionals)

# === Légende cockpitifiée ===
st.markdown("---")
st.subheader("📘 Légende des États cockpitifiés")
st.markdown("""
- ✅ **Fait** : Composant créé, opérationnel ou documenté.
- ⏳ **À mettre à jour / enrichir / compiler** : Nécessite une action cockpit.
- ❓ **À vérifier / envisager / proposer** : Statut incertain ou suggestion future.
- 🚫 **Non pertinent** : Écarté du périmètre cockpit souverain.
""")

# === Export cockpitifié ===
st.markdown("---")
st.subheader("📤 Export cockpitifié")

full_df = pd.concat([df_readme, df_manifest, df_components, df_optionals], ignore_index=True)

col1, col2, col3 = st.columns(3)
with col1:
    csv = full_df.to_csv(index=False).encode("utf-8")
    st.download_button("📎 Télécharger CSV", csv, "cockpit_tracker.csv", mime="text/csv")

with col2:
    yaml_data = yaml.dump(full_df.to_dict(orient="records"), allow_unicode=True, sort_keys=False)
    st.download_button("📎 Télécharger YAML", yaml_data.encode("utf-8"), "cockpit_tracker.yaml", mime="text/yaml")

with col3:
    md_data = "\n".join(
        f"- **{row['Nom']}** ({row['Type']}) — {row['Rôle cockpit']} — {row['État']}"
        for _, row in full_df.iterrows()
    )
    st.download_button(
        label="📎 Télécharger Markdown",
        data=md_data.encode("utf-8"),
        file_name="cockpit_tracker.md",
        mime="text/markdown"
    )
