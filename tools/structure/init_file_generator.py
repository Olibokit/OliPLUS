import os
import logging

# 📁 Dossier racine du projet
root_dir = "oliplus"

# 🔢 Compteur de fichiers créés
init_file_count = 0

# ⚠️ Liste des erreurs
errors = []

# 🧭 Dossiers à ignorer
IGNORED_DIRS = {"__pycache__", ".git", "venv", "node_modules"}

# 📝 Configuration du logger
logging.basicConfig(level=logging.INFO, format="📍 %(message)s")

logging.info(f"🔍 Parcours du dossier racine : {root_dir}")

# 🔄 Parcours récursif
for dirpath, dirnames, filenames in os.walk(root_dir):
    # ⛔ Ignore les dossiers non pertinents
    if any(ignored in dirpath.split(os.sep) for ignored in IGNORED_DIRS):
        continue

    init_file_path = os.path.join(dirpath, "__init__.py")

    try:
        # 📦 Création du fichier si manquant
        if not os.path.exists(init_file_path):
            with open(init_file_path, "w") as f:
                f.write("# Automatically generated __init__.py\n")
            init_file_count += 1
            logging.info(f"✅ Créé : {init_file_path}")

        # 🧪 Vérification explicite
        if "__init__.py" not in os.listdir(dirpath):
            errors.append(f"❌ Manquant dans : {dirpath}")

    except Exception as e:
        errors.append(f"⚠️ Erreur dans {dirpath} : {str(e)}")

# 📊 Résumé final
print(f"\n📦 Total __init__.py créés : {init_file_count}")
if errors:
    print("\n🚨 Problèmes rencontrés :")
    for error in errors:
        print(error)
else:
    print("\n✅ Tous les dossiers sont bien reconnus comme packages Python.")
