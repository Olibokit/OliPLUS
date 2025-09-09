from pathlib import Path
import subprocess
import sys

def install_requirements(requirements_dir: str = "requirements", full_file: str = "txt/requirements.full.txt"):
    req_path = Path(requirements_dir)
    full_path = Path(full_file)

    # 📁 Vérification du dossier requirements
    if not req_path.exists():
        print(f"❌ Dossier introuvable : {requirements_dir}")
        sys.exit(1)

    # 🔧 Étape 1 : Compilation des fichiers .in → .txt
    in_files = sorted(req_path.glob("*.in"))
    if not in_files:
        print("⚠️ Aucun fichier .in trouvé à compiler.")
    else:
        for in_file in in_files:
            txt_file = in_file.with_suffix(".txt")
            print(f"🔧 Compilation cockpit : {in_file.name} → {txt_file.name}")
            try:
                subprocess.run([
                    "pip-compile",
                    str(in_file),
                    "--output-file",
                    str(txt_file),
                    "--upgrade"
                ], check=True)
            except subprocess.CalledProcessError:
                print(f"❌ Erreur lors de la compilation de {in_file.name}")
                sys.exit(1)

    # 📦 Étape 2 : Installation des fichiers .txt dans requirements/
    txt_files = sorted(req_path.glob("*.txt"))
    for txt_file in txt_files:
        print(f"📦 Installation cockpit : {txt_file.name}")
        try:
            subprocess.run([
                "pip",
                "install",
                "-r",
                str(txt_file)
            ], check=True)
        except subprocess.CalledProcessError:
            print(f"❌ Erreur lors de l’installation de {txt_file.name}")
            sys.exit(1)

    # 📦 Étape 3 : Installation du fichier requirements.full.txt dans txt/
    if full_path.exists():
        print(f"📦 Installation cockpit : {full_path.name}")
        try:
            subprocess.run([
                "pip",
                "install",
                "-r",
                str(full_path)
            ], check=True)
        except subprocess.CalledProcessError:
            print(f"❌ Erreur lors de l’installation de {full_path.name}")
            sys.exit(1)
    else:
        print(f"⚠️ Fichier non trouvé : {full_path}")

    total = len(txt_files) + int(full_path.exists())
    print(f"✅ Installation cockpit terminée : {total} fichier(s) traité(s).")

if __name__ == "__main__":
    install_requirements()
