# 📘 dashboard_generator.py — Générateur cockpit HTML dynamique enrichi
import json
import yaml
import webbrowser
from pathlib import Path
from datetime import datetime

# === 📁 BLOC PATHS COCKPITIFIÉS ===
ROOT = Path(__file__).resolve().parent
TEMPLATE_HTML = ROOT / "dashboard" / "oliplus-dashboard-dynamic.html"
OUTPUT_DIR = ROOT / "oliplus_data" / "dashboard"
DATESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M")
OUTPUT_FILE = OUTPUT_DIR / f"dashboard_{DATESTAMP}.html"

# === 🗂️ SOURCES MULTIPLES INJECTÉES ===
SOURCES = {
    "oliplus": ROOT / "oliplus_data" / "inventaire_logiciels.json",
    "a_travailler": ROOT / "oliplus_data" / "inventaire_a_travailler.json",
    "fusion_manifest": ROOT / "cockpit_docs" / "fusion_manifest.yaml"
}

PLACEHOLDER = "/*__DATA_PLACEHOLDER__*/"

def load_source(path: Path) -> dict | list:
    try:
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ⚠️ Erreur parsing {path.name} : {e}")
    return []

def main():
    print("📊 Construction cockpit du dashboard dynamique...")

    if not TEMPLATE_HTML.exists():
        print(f"❌ Template HTML introuvable : {TEMPLATE_HTML}")
        return

    print("📥 Lecture des inventaires cockpit :")
    combined_data = {}
    for key, path in SOURCES.items():
        if path.exists():
            print(f"  ✅ {key} → {path.name}")
            combined_data[key] = load_source(path)
        else:
            print(f"  ⚠️ {key} manquant → {path.name}")
            combined_data[key] = []

    html = TEMPLATE_HTML.read_text(encoding="utf-8")

    if PLACEHOLDER not in html:
        print(f"⚠️ Placeholder `{PLACEHOLDER}` non trouvé dans le template.")
        return

    print("🧬 Injection des données cockpit...")
    enriched_json = json.dumps(combined_data, indent=2, ensure_ascii=False)
    html = html.replace(PLACEHOLDER, f"window.DATA = {enriched_json};")

    print("💾 Écriture du dashboard cockpit enrichi...")
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(html, encoding="utf-8")
        print(f"✅ Dashboard cockpit généré : {OUTPUT_FILE.name}")
    except Exception as e:
        print(f"❌ Erreur d’écriture du fichier : {e}")
        return

    print("🌐 Ouverture dans le navigateur...")
    try:
        webbrowser.open(OUTPUT_FILE.as_uri())
    except Exception:
        print("🧭 Ouvre le fichier manuellement dans ton navigateur.")

if __name__ == "__main__":
    main()
