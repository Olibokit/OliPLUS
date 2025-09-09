import os
import shutil
import glob
import yaml

CONFIG_FILE = "config_restart.yaml"

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["restart"]

def log(message, log_path):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)

def check_restart_files(path, name):
    return glob.glob(os.path.join(path, name + "*"))

def restart(config):
    restart_files = check_restart_files(config["path"], config["name"])
    if not restart_files:
        log("❌ Aucun fichier de redémarrage trouvé.", config["log_file"])
        return

    for file in restart_files:
        dest = os.getcwd()
        shutil.copy(file, dest)
        log(f"✅ Copié : {file} → {dest}", config["log_file"])

def main():
    config = load_config()
    if config["enabled"]:
        log("🔁 Redémarrage activé", config["log_file"])
        restart(config)
    else:
        log("⛔ Redémarrage désactivé", config["log_file"])

if __name__ == "__main__":
    main()
