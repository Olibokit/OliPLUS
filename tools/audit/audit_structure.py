"""
audit_structure.py — Audit intelligent des fichiers cockpit
Fonctions : structure, nommage, extensions, sécurité
"""
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import typer

# ─── Configuration cockpit typée ──────────────────────────────────────────────
DOSSIERS_SENSIBLES: List[str] = ["assets", "public", "temp", "archives", "old"]
EXTENSIONS_CRITIQUES: List[str] = [".sh", ".bat", ".exe"]
EXTENSIONS_IGNOREES: List[str] = [".log", ".trace", ".tmp"]
NOM_PREFIXES_INADAPTÉS: List[str] = ["copie_", "test_", "Document", "Nouveau"]
SEUIL_TRES_LEGER: int = 300  # octets

stats_audit: Dict[str, any] = {
    "total_fichiers": 0,
    "detectes": 0,
    "ignores": 0,
    "par_type": {},
    "alertes": []
}

# ─── Fonctions d'affichage cockpit ────────────────────────────────────────────

def echo_info(msg: str) -> None: typer.secho(msg, fg=typer.colors.BLUE)
def echo_warn(msg: str) -> None: typer.secho(msg, fg=typer.colors.YELLOW)
def echo_err(msg: str) -> None: typer.secho(msg, fg=typer.colors.RED)
def echo_ok(msg: str) -> None: typer.secho(msg, fg=typer.colors.GREEN)

# ─── Audit individuel cockpit ─────────────────────────────────────────────────

def audit_structure(file_path: Path, detected_type: Optional[str] = None) -> None:
    stats_audit["total_fichiers"] += 1
    rel_path = file_path.as_posix()
    alerts: List[str] = []

    # 🔐 Fichier de config dans un dossier public
    if "config" in file_path.name.lower() and "public" in rel_path.lower():
        alerts.append("🔐 config exposé publiquement")

    # ⚠️ Script à risque dans zone sensible
    for dossier in DOSSIERS_SENSIBLES:
        if f"/{dossier}/" in rel_path.replace("\\", "/") and file_path.suffix.lower() in EXTENSIONS_CRITIQUES:
            alerts.append(f"⚠️ {file_path.suffix} dans dossier sensible ({dossier})")

    # 🧨 Extension critique
    if file_path.suffix.lower() in EXTENSIONS_CRITIQUES:
        alerts.append(f"🧨 Extension exécutable inhabituelle : {file_path.suffix}")

    # 📛 Nommage peu informatif
    if any(file_path.stem.lower().startswith(pfx.lower()) for pfx in NOM_PREFIXES_INADAPTÉS):
        alerts.append(f"📛 Nom peu informatif : {file_path.name}")

    # 📄 Poids très léger
    try:
        if file_path.stat().st_size < SEUIL_TRES_LEGER:
            alerts.append(f"📄 Fichier très léger (<{SEUIL_TRES_LEGER}B)")
    except Exception as e:
        alerts.append(f"⚠️ Impossible de lire la taille du fichier : {e}")

    # 🔎 Extension ignorée
    if file_path.suffix.lower() in EXTENSIONS_IGNOREES:
        stats_audit["ignores"] += 1
        return

    if alerts:
        stats_audit["alertes"].append((file_path.name, alerts))

    # 🧩 Stat par type cockpit détecté
    if detected_type:
        stats_audit["par_type"].setdefault(detected_type, 0)
        stats_audit["par_type"][detected_type] += 1
        stats_audit["detectes"] += 1
    else:
        stats_audit["ignores"] += 1

# ─── Résumé cockpit final ─────────────────────────────────────────────────────

def afficher_resume_audit(export_md: bool = False, md_path: str = "audit_alertes.md") -> None:
    typer.echo("\n📊 Résumé du scan cockpit")
    typer.echo(f"• Total analysés : {stats_audit['total_fichiers']}")
    typer.echo(f"• Classés cockpit : {stats_audit['detectes']}")
    typer.echo(f"• Ignorés (non typés ou logs) : {stats_audit['ignores']}")

    if stats_audit["par_type"]:
        typer.echo("\n🧩 Répartition par type cockpit :")
        for t, n in stats_audit["par_type"].items():
            typer.echo(f"  - {t} : {n}")

    if stats_audit["alertes"]:
        typer.echo("\n🚨 Alertes détectées :")
        for fname, notes in stats_audit["alertes"]:
            typer.echo(f"  ▶ {fname}")
            for note in notes:
                typer.echo(f"     {note}")
        if export_md:
            markdown_alertes(stats_audit["alertes"], md_path)
    else:
        echo_ok("✅ Aucun problème détecté dans les fichiers scannés.")

# ─── Export Markdown cockpit (optionnel) ──────────────────────────────────────

def markdown_alertes(alertes: List[Tuple[str, List[str]]], out_file: str = "audit_alertes.md") -> None:
    lines: List[str] = [
        "# 🚨 Audit cockpit — Alertes détectées\n",
        f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "| Fichier | Problèmes détectés |",
        "|---------|--------------------|"
    ]
    for fname, notes in alertes:
        lines.append(f"| `{fname}` | {' / '.join(notes)} |")
    Path(out_file).write_text("\n".join(lines), encoding="utf-8")
    echo_warn(f"📝 Rapport Markdown exporté → {out_file}")
