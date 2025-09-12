import json
from pathlib import Path
from collections import Counter
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = ROOT / "A travailler" / "dashboard"
INVENTAIRE = DASHBOARD_DIR / "inventaire_fusionne.json"
RAPPORT = DASHBOARD_DIR / "rapport_exploration.yaml"

def charger_inventaire():
    if not INVENTAIRE.exists():
        print("❌ Fichier introuvable :", INVENTAIRE)
        return []
    try:
        with INVENTAIRE.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print("❌ Erreur de lecture JSON :", e)
        return []

def analyser_fragments(data):
    stats = {
        "total": len(data),
        "par_statut": Counter(),
        "par_source": Counter(),
        "nouveaux": 0,
        "liés_au_catalogue": 0,
        "dates": []
    }

    for item in data:
        stats["par_statut"][item.get("statut", "inconnu")] += 1
        stats["par_source"][item.get("source_logicielle", "non spécifiée")] += 1
        if item.get("est_nouveau"):
            stats["nouveaux"] += 1
        if item.get("catalogue_reference"):
            stats["liés_au_catalogue"] += 1
        if item.get("date_ajout"):
            stats["dates"].append(item["date_ajout"])

    return stats

def générer_rapport(stats):
    lignes = [
        f"date_analyse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"total_fragments: {stats['total']}",
        f"nouveaux: {stats['nouveaux']}",
        f"liés_au_catalogue: {stats['liés_au_catalogue']}",
    ]

    if stats["dates"]:
        dates_sorted = sorted(stats["dates"])
        lignes.append(f"plage_dates: {dates_sorted[0]} → {dates_sorted[-1]}")

    lignes.append("statuts:")
    for statut, count in sorted(stats["par_statut"].items()):
        lignes.append(f"  {statut}: {count}")

    lignes.append("sources:")
    for source, count in sorted(stats["par_source"].items()):
        lignes.append(f"  {source}: {count}")

    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(lignes), encoding="utf-8")
    print(f"✅ Rapport cockpit généré : {RAPPORT.relative_to(ROOT)}")

if __name__ == "__main__":
    data = charger_inventaire()
    if data:
        stats = analyser_fragments(data)
        générer_rapport(stats)
