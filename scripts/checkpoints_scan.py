from pathlib import Path

CHECKPOINTS = {
    "Fragments": Path("OliPLUS/6000_INFORMATION_ET_COMMUNICATIONS/1100_GOUVERNANCE_INFORMATION/section_fragments.md"),
    "Dashboard HTML": Path("OliPLUS/6000_INFORMATION_ET_COMMUNICATIONS/1300_DASHBOARDS/oliplus-dashboard-dynamic.html"),
    "Payload JS": Path("OliPLUS/6000_INFORMATION_ET_COMMUNICATIONS/1300_DASHBOARDS/payload.js"),
    "Classification plan": Path("OliPLUS/6000_INFORMATION_ET_COMMUNICATIONS/1100_GOUVERNANCE_INFORMATION/classification_plan.yaml")
}

print("🔎 Vérification cockpit des fichiers déployés\n")

ok_files = []
missing_files = []

for label, path in CHECKPOINTS.items():
    if path.exists():
        print(f"✅ {label} : OK")
        ok_files.append(label)
    else:
        print(f"❌ {label} manquant ({path})")
        missing_files.append(label)

# Résumé cockpit
print("\n📘 Résumé cockpit déploiement :")
print(f"✅ {len(ok_files)} fichiers présents")
print(f"❌ {len(missing_files)} fichiers manquants")

if missing_files:
    print("\n🚨 Fichiers manquants à investiguer :")
    for label in missing_files:
        print(f" - {label}")
