from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, constr
from typing import Literal
import logging

router = APIRouter()

# 🧬 Schéma d'entrée typé
class LanguageUpdateRequest(BaseModel):
    language: Literal["fr", "en", "es", "de", "pt", "it", "ja", "zh"]

# 📘 Simule une mise à jour utilisateur (ex. via DB ou fichier YAML)
def set_user_language(user_id: str, language: str) -> bool:
    # 🔐 Exemple : mise à jour dans la base ou session
    logging.info(f"[Cockpit] Langue mise à jour pour {user_id}: {language}")
    return True

@router.post("/user/language", status_code=status.HTTP_200_OK)
def update_language(request: LanguageUpdateRequest, user_id: str):
    """
    🔤 Met à jour la langue cockpit préférée de l'utilisateur.
    🧾 Utilise un schéma typé pour restreindre les options valides.
    """
    success = set_user_language(user_id=user_id, language=request.language)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la mise à jour de la langue."
        )

    return {
        "message": "✅ Langue mise à jour avec succès.",
        "user_id": user_id,
        "language": request.language
    }
