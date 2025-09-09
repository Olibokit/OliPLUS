import logging
from core.tasks.base_backend import TaskBackend

logger = logging.getLogger(__name__)

class LocalTaskBackend(TaskBackend):
    """
    Backend cockpit local — utilisé pour le développement, les tests ou comme fallback.
    Simule l'exécution des tâches sans passer par un système distribué.
    """

    def submit(self, task: str, payload: dict) -> dict:
        logger.info(f"[LocalTask] Soumission de la tâche '{task}' avec payload : {payload}")

        # 💥 Simule une erreur pour certaines tâches (optionnel)
        if task == "simulate_error":
            logger.warning(f"[LocalTask] Échec simulé pour la tâche '{task}'")
            return {"status": "error", "message": "Erreur simulée dans le backend local"}

        # 🧪 Mock de résultat selon le type de tâche
        result = self._mock_result(task, payload)

        logger.debug(f"[LocalTask] Résultat simulé : {result}")
        return {"status": "ok", "task": task, "result": result}

    def _mock_result(self, task: str, payload: dict) -> dict:
        """
        Génère un résultat simulé en fonction du type de tâche.
        Peut être enrichi selon les besoins du cockpit.
        """
        if task.startswith("email."):
            return {"sent": True, "to": payload.get("to")}
        elif task.startswith("user."):
            return {"user_id": payload.get("user_id"), "updated": True}
        else:
            return {"echo": payload}
