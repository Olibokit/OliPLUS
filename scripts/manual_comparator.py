import pandas as pd
import json
import logging
import argparse
from pathlib import Path
from typing import List

# 📘 Logger cockpit
logging.basicConfig(level=logging.INFO, format="📘 %(message)s")
logger = logging.getLogger("manual_comparator")

EXPECTED_COLUMNS = ["type", "statut", "cotation", "commentaire"]

def validate_columns(df: pd.DataFrame, source: str) -> bool:
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        logger.error(f"❌ Colonnes manquantes dans {source} : {missing}")
        return False
    return True

def load_manual(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        df.set_index("chemin relatif", inplace=True)
        if not validate_columns(df, "manuel"):
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.warning(f"❌ Erreur chargement manuel : {e}")
        return pd.DataFrame()

def load_simulated(path: Path) -> pd.DataFrame:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        df = pd.DataFrame(raw)
        df.set_index("chemin relatif", inplace=True)
        if not validate_columns(df, "simulé"):
            return pd.DataFrame()
        return df
    except Exception as e:
        logger.error(f"⚠️ Erreur chargement cockpit simulé : {e}")
        return pd.DataFrame()

def compare(manual_df: pd.DataFrame, simulated_df: pd.DataFrame, export_path: Path) -> None:
    # 🔎 Différences de présence
    missing_in_simulated = manual_df[~manual_df.index.isin(simulated_df.index)]
    missing_in_manual = simulated_df[~simulated_df.index.isin(manual_df.index)]

    # 🔍 Différences de valeurs
    common = manual_df.index.intersection(simulated_df.index)
    divergences: List[dict] = []
    for path in common:
        m = manual_df.loc[path]
        s = simulated_df.loc[path]
        diff = {}
        for col in EXPECTED_COLUMNS:
            if str(m[col]).strip() != str(s[col]).strip():
                diff[col] = f"Manuel: '{m[col]}' | Simulé: '{s[col]}'"
        if diff:
            divergences.append({
                "chemin_relatif": path,
                "type_divergence": ", ".join(diff.keys()),
                "details": diff
            })

    # 📊 Résumé
    logger.info("\n🎯 Résumé comparaison cockpit")
    logger.info(f"📁 Manuel : {len(manual_df)} éléments")
    logger.info(f"📂 Simulé : {len(simulated_df)} éléments")
    logger.info(f"➕ Manuels non trouvés : {len(missing_in_simulated)}")
    logger.info(f"➕ Simulés non dans le manuel : {len(missing_in_manual)}")
    logger.info(f"🔀 Divergences communes : {len(divergences)}")

    # 💾 Export CSV divergences
    if divergences:
        df_export = pd.DataFrame([{
            "chemin relatif": d["chemin_relatif"],
            "type divergence": d["type_divergence"],
            "details divergence": json.dumps(d["details"], ensure_ascii=False)
        } for d in divergences])
        df_export.to_csv(export_path, index=False, encoding="utf-8-sig")
        logger.info(f"🧩 Export divergences : {export_path.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="🔍 Comparateur cockpit manuel vs simulé")
    parser.add_argument("--manual", default="manual_pre_sorted_data.csv", help="Fichier CSV manuel")
    parser.add_argument("--simulated", default="cockpit_simulated.json", help="Fichier JSON simulé")
    parser.add_argument("--export", default="divergences_oliplus.csv", help="Nom du fichier exporté")
    args = parser.parse_args()

    manual_df = load_manual(Path(args.manual))
    simulated_df = load_simulated(Path(args.simulated))

    if manual_df.empty or simulated_df.empty:
        logger.error("❌ Comparaison impossible : données manquantes ou invalides.")
        return

    compare(manual_df, simulated_df, Path(args.export))

if __name__ == "__main__":
    main()
