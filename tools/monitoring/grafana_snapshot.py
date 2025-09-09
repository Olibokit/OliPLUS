import argparse
import requests
import logging
from typing import Optional

# 🔧 Logger cockpit
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("cockpit.grafana")

def create_snapshot(
    base_url: str,
    dashboard_uid: str,
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> Optional[str]:
    endpoint = f"{base_url.rstrip('/')}/api/snapshots"
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {"dashboard": {"uid": dashboard_uid}}

    try:
        if token:
            response = requests.post(endpoint, json=payload, headers=headers)
        else:
            response = requests.post(endpoint, json=payload, headers=headers, auth=(username, password))

        response.raise_for_status()
        snapshot_url = response.json().get("url")
        if snapshot_url:
            logger.info(f"📸 Snapshot disponible : {snapshot_url}")
            return snapshot_url
        else:
            logger.warning("⚠️ Réponse reçue mais pas d’URL de snapshot.")
            return None

    except requests.RequestException as e:
        logger.error(f"❌ Erreur lors de la création du snapshot : {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="📸 Crée un snapshot d’un dashboard Grafana")
    parser.add_argument("--url", default="http://localhost:3000", help="🌐 URL de Grafana")
    parser.add_argument("--uid", required=True, help="🆔 UID du dashboard")
    parser.add_argument("--token", help="🔐 Token d’API Grafana")
    parser.add_argument("--username", default="admin", help="👤 Nom d’utilisateur (si pas de token)")
    parser.add_argument("--password", default="admin", help="🔑 Mot de passe (si pas de token)")

    args = parser.parse_args()

    create_snapshot(
        base_url=args.url,
        dashboard_uid=args.uid,
        token=args.token,
        username=args.username,
        password=args.password
    )

if __name__ == "__main__":
    main()
