from datetime import datetime
from typing import Dict, List, Optional
from employee_dto import PunchInRequest, PunchOutRequest
from exceptions import PermissionDeniedError, ValidationError
import logging

# 🔧 Configuration du logger cockpit
logger = logging.getLogger("attendance")
logger.setLevel(logging.INFO)

attendance_log: Dict[str, List[Dict[str, Optional[datetime]]]] = {}

def punch_in(employee_id: str, timestamp: datetime) -> None:
    """
    Enregistre une entrée (punch in) pour un employé.

    Args:
        employee_id: Identifiant de l'employé
        timestamp: Date et heure d'entrée

    Raises:
        ValidationError: si l'entrée chevauche une absence ou une entrée existante
    """
    if employee_id not in attendance_log:
        attendance_log[employee_id] = []

    # 🧠 Vérification de chevauchement (à intégrer avec leave_service plus tard)
    last_entry = attendance_log[employee_id][-1] if attendance_log[employee_id] else None
    if last_entry and 'out' not in last_entry:
        raise ValidationError("⛔ Punch in déjà actif sans punch out.")

    attendance_log[employee_id].append({'in': timestamp})
    logger.info(f"✅ Punch in enregistré pour {employee_id} à {timestamp.isoformat()}")

def punch_out(employee_id: str, timestamp: datetime) -> None:
    """
    Enregistre une sortie (punch out) pour un employé.

    Args:
        employee_id: Identifiant de l'employé
        timestamp: Date et heure de sortie

    Raises:
        PermissionDeniedError: si aucun punch in n'est actif
    """
    if employee_id in attendance_log and attendance_log[employee_id]:
        last_entry = attendance_log[employee_id][-1]
        if 'out' in last_entry:
            raise ValidationError("⛔ Punch out déjà effectué pour cette session.")
        last_entry['out'] = timestamp
        logger.info(f"✅ Punch out enregistré pour {employee_id} à {timestamp.isoformat()}")
    else:
        raise PermissionDeniedError("Punch out sans punch in.")

def get_attendance(employee_id: str) -> List[Dict[str, Optional[datetime]]]:
    """
    Retourne l'historique de présence d'un employé.

    Args:
        employee_id: Identifiant de l'employé

    Returns:
        Liste des sessions de présence (in/out)
    """
    return attendance_log.get(employee_id, [])
