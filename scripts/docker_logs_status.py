#!/usr/bin/env python3
# 📖 Lecture cockpit du fichier docker_logs_status.json + option dry-run

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

DEFAULT_STATUS_FILE = Path("docker_logs_status.json")

def load_status(file_path: Path) -> List[Dict]:
    if not file_path.exists():
        print(f"❌ Fichier introuvable : {file_path}")
        exit(1)
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠️ Erreur de lecture JSON : {e}")
        exit(1)

def display_table(data: List[Dict]):
    print("\n📊 État cockpit des logs Docker\n")
    print(f"{'Container':<20} {'Driver':<12} {'Status':<30} {'Log Path'}")
    print("-" * 80)
    for item in data:
        print(f"{item['container']:<20} {item['log_driver']:<12} {item['status']:<30} {item['log_path']}")
    print()

def simulate_purge(data: List[Dict]):
    print("\n🧪 Simulation cockpit de purge des logs\n")
    purged, skipped = 0, 0

    for item in data:
        name = item.get("container", "inconnu")
        driver = item.get("log_driver", "unknown")
        path = item.get("log_path", "null")
        status = item.get("status", "indéfini")

        if driver != "json-file":
            print(f"⏭️ {name} — pilote non compatible : {driver}")
            skipped += 1
        elif path == "null" or not Path(path).exists():
            print(f"⏭️ {name} — log inaccessible ou introuvable")
            skipped += 1
        else:
            print(f"🔄 Simulation : purge cockpit de {name} → {path}")
            purged += 1

    print(f"\n✅ Simulation terminée : {purged} purge(s) simulée(s), {skipped} ignorée(s).\n")

def main():
    parser = argparse.ArgumentParser(description="📖 Lecture cockpit des logs Docker")
    parser.add_argument("--dry-run", action="store_true", help="🔍 Simuler la purge sans modifier les fichiers")
    parser.add_argument("--file", type=Path, default=DEFAULT_STATUS_FILE, help="📁 Fichier JSON à analyser")
    args = parser.parse_args()

    data = load_status(args.file)

    if args.dry_run:
        simulate_purge(data)
    else:
        display_table(data)

if __name__ == "__main__":
    main()
