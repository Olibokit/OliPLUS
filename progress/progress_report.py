import json
from pathlib import Path
from datetime import datetime

PROGRESS_PATH = Path("progress/progress.json")

def main():
    if not PROGRESS_PATH.exists():
        print(f"❌ Fichier introuvable : {PROGRESS_PATH}")
        return

    with PROGRESS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    phases = {}
    for bloc in data:
        key = (bloc["univers"], bloc["phase"])
        phases.setdefault(key, []).append(bloc)

    print(f"\n🧭 Rapport cockpit — {datetime.now():%Y-%m-%d %H:%M:%S}")

    for (univers, phase), blocs in sorted(phases.items()):
        total = len(blocs)
        done = sum(1 for b in blocs if b["statut"].startswith("✅"))
        percent = round((done / total) * 100) if total else 0

        print(f"\n📦 [{univers}] Phase : {phase}")
        print(f"   ✅ {done}/{total} blocs complétés ({percent}%)")

        for bloc in sorted(blocs, key=lambda b: b["bloc"]):
            print(f"   {bloc['statut']} {bloc['bloc']}")

if __name__ == "__main__":
    main()
