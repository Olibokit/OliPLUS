from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, constr
from datetime import datetime, timedelta

router = APIRouter()

# 📦 Modèle de requête cockpit
class LicenseRequest(BaseModel):
    key: constr(min_length=10, max_length=64)

# 📦 Modèle de réponse cockpit
class LicenseResponse(BaseModel):
    valid: bool
    message: str
    expires_at: str | None = None

# 🗂️ Registre simulé des licences cockpit
LICENSE_REGISTRY = {
    "OLI-VALID-123456": {
        "expires_at": datetime(2025, 12, 31),
        "note": "Licence cockpit standard"
    },
    "OLI-PRO-789012": {
        "expires_at": datetime.now() + timedelta(days=180),
        "note": "Licence cockpit PRO temporaire"
    }
}

# 🔐 Endpoint de vérification cockpit
@router.post("/license/verify", response_model=LicenseResponse)
def verify_instance(payload: LicenseRequest):
    key = payload.key.strip()

    # 🧠 Vérification du préfixe cockpit
    if not key.startswith("OLI-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clé de licence invalide : préfixe 'OLI-' requis."
        )

    # 🔍 Recherche dans le registre cockpit
    license_info = LICENSE_REGISTRY.get(key)
    if license_info:
        return LicenseResponse(
            valid=True,
            message=f"✅ {license_info['note']}.",
            expires_at=license_info["expires_at"].isoformat()
        )

    # ❌ Licence non reconnue
    return LicenseResponse(
        valid=False,
        message="❌ Licence cockpit non reconnue ou expirée.",
        expires_at=None
    )
