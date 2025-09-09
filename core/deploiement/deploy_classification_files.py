from pathlib import Path
from datetime import datetime

def deploy_classification_files(log_only=False, log_dir=None):
    """
    Déploie les fichiers de classification documentaire (simulation cockpitifiée).
    
    - Crée un log horodaté dans le répertoire de gouvernance ou personnalisé
    - Retourne le contenu du log pour affichage ou journalisation

    Args:
        log_only (bool): Si True, ne crée pas physiquement les fichiers (dry run)
        log_dir (str or Path): Répertoire personnalisé pour le journal (optionnel)

    Returns:
        str: texte du journal simulé de déploiement
    """

    timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')
    log_lines = [
        f"🕒 [{timestamp}] Déploiement cockpit déclenché",
        "📦 YAML classification copié dans la structure OliPLUS",
        "📊 Export CSV synchronisé pour consultation",
        "📘 Markdown mis à jour pour l’affichage documentation",
        "🌳 Arborescence GDA en place",
        "✅ Fin du déploiement cockpitifié",
        "───────────────",
        f"🔢 Total actions simulées : 4"
    ]
    log_text = "\n".join(log_lines)

    if not log_only:
        # Définir le chemin du journal
        log_folder = Path(log_dir) if log_dir else Path("6000_INFORMATION_ET_COMMUNICATIONS") / "1100_GOUVERNANCE_INFORMATION"
        log_folder.mkdir(parents=True, exist_ok=True)
        log_file = log_folder / f".copilot_classification_{timestamp}.log"
        log_file.write_text(log_text, encoding="utf-8")

    return log_text
