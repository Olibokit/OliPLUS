# 📝 CHANGELOG – OliPLUS

Toutes les étapes importantes du développement logiciel.

## [0.2.0] – 2025-06-26
### ✨ Nouvelles fonctionnalités
- Ajout du moteur typologique `ClassificationService` avec export CSV et CLI
- Génération automatique de dataclasses avec `generate_oliplus_models.py`
- Script de nettoyage interactif pour `oliplus_reference/` (`reference_cleaner.py`)
- Modèle `Document` cockpit-ready : support, cycle de vie, archivabilité
- Intégration de `DocumentAdmin`, `as_dict()`, et `slug` auto dans les modèles
- Script `check_env.py` pour validation sécurisée des variables d’environnement `.env`
- Optimisation cockpit du `asgi.py` et du fichier `urls.py`

### 🔧 Améliorations techniques
- Uniformisation des chemins relatifs dans `oliplus_toolchain/`
- Injection dynamique de `.gitkeep` via script PowerShell (`init_git_folders.ps1`)
- Script batch `sync-menu.bat` pour lancement immédiat d’une action OliPLUS
- Logging ASGI configurable (fichier + stderr, niveau personnalisable)

### 🐛 Correctifs
- Correction de certains chemins de migration absents dans Git
- Sécurisation de l’accès aux fichiers YAML malformés
- Nettoyage des fichiers obsolètes ou ambigus dans `oliplus_reference/`

---

## [0.1.0] – 2025-06-12
- Création de la structure du projet (`OliPLUS/`)
- Ajout des dossiers `backend/`, `frontend/`, `data/`, `scripts/`, `docs/`, `setup/`
- Génération des fichiers initiaux : `README.md`, `structure.md`, `CHANGELOG.md`
- Adoption du nom officiel **OliPLUS** 🎉
- Début du recensement via `list_files.py` et planification via `structure.md`
