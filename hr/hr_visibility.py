from typing import Set
from datetime import datetime
import logging

# 💾 Cache local
_hr_visible_cache: dict[int, Set[int]] = {}

def get_visible_employee_ids(user: User) -> Set[int]:
    """
    🔍 Retourne les IDs des employés visibles pour un utilisateur HR cockpit :
    - soi-même
    - subordonnés directs
    - subordonnés indirects (si chef de structure)
    - superviseurs indirects (champ JSON)
    - tous les employés si accès complet
    - filtrage des données sensibles
    - avec cache et journalisation
    """
    if user.has_full_employee_access:
        ids = {e.id for e in get_all_employees()}
        log_hr_visibility(user.id, len(ids))
        return ids

    if user.id in _hr_visible_cache:
        return _hr_visible_cache[user.id]

    ids = {user.employee_id}

    # ➕ Subordonnés directs
    directs = get_all_employees(supervisor_id=user.employee_id)
    ids.update(e.id for e in directs)

    # ➕ Subordonnés indirects via structure
    if user.is_department_head:
        children = get_children_departments(user.department_id)
        for dep_id in children:
            indirects = get_all_employees(department_id=dep_id)
            ids.update(e.id for e in indirects if e.id != user.employee_id)

    # ➕ Superviseurs indirects via champ JSON
    for emp in get_all_employees():
        if getattr(emp, "indirect_supervisors", []) and user.employee_id in emp.indirect_supervisors:
            ids.add(emp.id)

    # 🔒 Filtrage sensible
    ids = filter_sensitive_employees(ids)

    # 🧠 Mise en cache
    _hr_visible_cache[user.id] = ids

    # 📝 Audit
    log_hr_visibility(user.id, len(ids))

    return ids


def invalidate_hr_cache(user_id: int):
    """🔁 Invalide le cache HR pour un utilisateur."""
    _hr_visible_cache.pop(user_id, None)


def invalidate_hr_cache_on_employee_update(emp_id: int):
    """⚙️ Purge le cache pour les utilisateurs impactés par une mise à jour d’un employé."""
    affected = get_users_related_to_employee(emp_id)
    for user in affected:
        invalidate_hr_cache(user.id)


def filter_sensitive_employees(ids: Set[int]) -> Set[int]:
    """🛡️ Retire les employés sensibles."""
    return {
        e.id for e in get_employees_by_ids(ids)
        if not getattr(e, "is_sensitive_data", False)
    }


def log_hr_visibility(user_id: int, size: int):
    """📝 Journalise les accès HR cockpit."""
    logging.basicConfig(filename="hr_access.log", level=logging.INFO)
    logging.info(f"[{datetime.now().isoformat()}] HR user {user_id} → {size} employés visibles")
