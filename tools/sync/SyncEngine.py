import os
import json
import yaml
import pkg_resources
import networkx as nx
from pathlib import Path

class SyncEngine:
    """
    🧠 Moteur cockpitifié de synchronisation modulaire
    - Scan des fichiers
    - Chargement de configuration
    - Construction de graphe de dépendances
    - Vérification des scripts, extensions et dépendances
    """

    SUPPORTED_EXTENSIONS = [".py", ".json", ".cfg", ".yaml", ".yml", ".html", ".css", ".ps1", ".sql"]

    def __init__(self, project_path, config_path=None):
        self.project_path = Path(project_path)
        self.config_path = Path(config_path) if config_path else None
        self.graph = nx.DiGraph()
        self.modules = []
        self.config = {}
        if self.config_path:
            self.load_config()

    # 🔗 Chargement du fichier de configuration cockpit
    def load_config(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                if self.config_path.suffix in [".yaml", ".yml"]:
                    self.config = yaml.safe_load(f)
                else:
                    self.config = json.load(f)
        except Exception as e:
            print(f"❌ Erreur de chargement du fichier de config : {e}")
            self.config = {}

    # 🔍 Scan cockpitifié des fichiers du projet
    def run_scan(self):
        self.modules.clear()
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.modules.append(file_path)

    # 🧠 Construction du graphe de dépendances cockpit
    def build_graph(self):
        self.graph.clear()
        for module in self.modules:
            self.graph.add_node(str(module))
            if module.suffix == ".json":
                try:
                    with open(module, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        deps = data.get("dependencies", [])
                        for dep in deps:
                            dep_path = self.project_path / dep
                            self.graph.add_edge(str(module), str(dep_path))
                except Exception as e:
                    print(f"⚠️ Erreur dans le fichier {module.name} : {e}")
                    continue

    # 🚨 Détection cockpitifiée des liens manquants
    def resolve_missing_links(self):
        return [n for n in self.graph.nodes if not Path(n).exists()]

    # 📊 Visualisation cockpitifiée du graphe (format DOT)
    def visualize_graph(self):
        dot = "digraph G {\n"
        for src, dst in self.graph.edges:
            dot += f'"{Path(src).name}" -> "{Path(dst).name}";\n'
        dot += "}"
        return dot

    # ✅ Vérifie que tous les scripts du dashboard existent
    def check_dashboard_scripts(self):
        missing = []
        scripts = self.config.get("dashboardScripts", {})
        for name, script in scripts.items():
            script_path = self.project_path / script
            if not script_path.exists():
                missing.append((name, script))
        return missing

    # ✅ Compare les extensions activées avec les fichiers présents
    def check_extension_mismatch(self):
        ext_folder = self.project_path / self.config.get("extensions", {}).get("scanFolder", "extensions")
        enabled = self.config.get("extensions", {}).get("enabled", {})
        found = [f.stem for f in ext_folder.glob("*.py")]
        return [e for e in found if not enabled.get(e, False)]

    # ✅ Compare les versions installées avec celles requises
    def check_python_dependencies(self):
        required = self.config.get("dependencies", {})
        issues = []
        for pkg, req_version in required.items():
            try:
                installed = pkg_resources.get_distribution(pkg).version
                if pkg_resources.parse_version(installed) < pkg_resources.parse_version(req_version.replace(">=", "")):
                    issues.append((pkg, installed, req_version))
            except Exception:
                issues.append((pkg, "non installé", req_version))
        return issues
