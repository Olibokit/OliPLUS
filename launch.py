import subprocess
import time
import webbrowser
import socket
import json
import os
import sys

# 📦 Configuration cockpitifiée
CONFIG_FILE = "launch.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("❌ Fichier de configuration 'launch.json' introuvable.")
        sys.exit(1)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("localhost", port)) == 0

def launch_docker(compose_file):
    print("🚀 Lancement des services cockpitifiés...")
    subprocess.run(["docker-compose", "-f", compose_file, "up", "--build", "-d"])

def wait_for_services(services):
    print("⏳ Vérification des services...")
    for service in services:
        print(f"🔍 Attente du service : {service}")
        for _ in range(10):
            result = subprocess.run(
                ["docker", "inspect", "--format={{.State.Health.Status}}", service],
                capture_output=True, text=True
            )
            if "healthy" in result.stdout:
                print(f"✅ {service} est prêt.")
                break
            time.sleep(2)
        else:
            print(f"⚠️ {service} n’a pas répondu à temps.")

def open_ui(port, auto_open):
    if not auto_open:
        return
    print(f"🌐 Ouverture de l’interface cockpitifiée sur http://localhost:{port}")
    for _ in range(30):
        if is_port_open(port):
            webbrowser.open(f"http://localhost:{port}")
            return
        time.sleep(1)
    print("⚠️ L’interface n’a pas démarré à temps.")

def main():
    config = load_config()
    compose_file = config.get("docker_compose", "docker-compose.yaml")
    services = config.get("services", [])
    port = config.get("streamlit_port", 8501)
    auto_open = config.get("open_browser", True)

    launch_docker(compose_file)
    wait_for_services(services)
    open_ui(port, auto_open)

if __name__ == "__main__":
    main()
