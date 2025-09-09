# 📘 dashboard_ui_view.py — Interface Streamlit du cockpit HTML Oliplus
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from typing import Optional
from datetime import datetime

def render(html_path: Path = Path("dashboard/oliplus-dashboard-dynamic.html")) -> None:
    st.set_page_config(page_title="Cockpit HTML Oliplus", page_icon="📊", layout="wide")
    st.title("📊 Interface cockpit visuelle (HTML dynamique)")

    st.markdown(
        """
        Ce module embarque dynamiquement le tableau de bord HTML (`.html`) généré par la chaîne
        `structure → payload → injection JS`. Il permet de consulter l’état documentaire cockpit
        et les visualisations typées (arborescence, fiches, fusion logicielle, indicateurs).
        """
    )

    st.divider()

    # 📄 Saisie du chemin HTML
    html_path_str: str = st.text_input("📄 Chemin vers le fichier HTML", value=str(html_path))
    html_path = Path(html_path_str.strip())

    # 📐 Choix de la hauteur d'affichage
    dashboard_height: int = st.slider("📐 Hauteur du tableau cockpit (px)", min_value=800, max_value=2000, value=1300)

    # 🧪 Option de rechargement manuel
    if st.button("🔄 Recharger le tableau HTML"):
        st.experimental_rerun()

    # 📡 Chargement sécurisé avec feedback enrichi
    with st.spinner("📡 Chargement du tableau cockpit en cours..."):
        if html_path.is_file() and html_path.suffix.lower() == ".html":
            try:
                html_content: str = html_path.read_text(encoding="utf-8")
                components.html(html_content, height=dashboard_height, scrolling=True)
                st.success("✅ Tableau de bord cockpit chargé avec succès.")
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
        else:
            st.error("❌ Fichier HTML introuvable ou extension non supportée.")
            st.markdown(f"🔎 Chemin fourni : `{html_path.resolve()}`")
            st.caption("💡 Vérifie que le fichier existe et a été généré avec `dashboard_html_launcher.py`.")

    # 📦 Méta-informations enrichies
    if html_path.exists():
        mod_time = datetime.fromtimestamp(html_path.stat().st_mtime)
        st.markdown(f"🕓 Dernière modification : `{mod_time.isoformat()}`")
        st.markdown(f"📦 Taille : `{html_path.stat().st_size / 1024:.1f} Ko`")

    # 🧾 Résumé visuel
    st.divider()
    st.markdown("### 📘 Résumé cockpit")
    st.markdown(
        f"""
        - **Fichier chargé** : `{html_path.name}`
        - **Chemin absolu** : `{html_path.resolve()}`
        - **Hauteur affichée** : `{dashboard_height}px`
        """
    )
