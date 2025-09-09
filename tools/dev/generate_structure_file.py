import os

EXCLUDED_NAMES = {"__pycache__", ".DS_Store", "oliPLUS_structure.txt"}

def is_excluded(name: str) -> bool:
    return name in EXCLUDED_NAMES or name.startswith(".")

def generate_structure_file(output_file: str = "oliPLUS_structure.txt") -> None:
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for root, dirs, files in os.walk("."):
                # Nettoyage des dossiers exclus
                dirs[:] = [d for d in dirs if not is_excluded(d)]
                files = [file for file in files if not is_excluded(file)]

                depth = root.count(os.sep)
                indent = "│   " * depth
                f.write(f"{indent}├── {os.path.basename(root)}/\n")

                for file in files:
                    file_indent = "│   " * (depth + 1)
                    f.write(f"{file_indent}└── {file}\n")

        print("✅ Fichier cockpit 'oliPLUS_structure.txt' généré avec succès.")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du fichier : {e}")

if __name__ == "__main__":
    generate_structure_file()
