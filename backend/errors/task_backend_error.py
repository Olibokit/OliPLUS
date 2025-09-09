from typing import Optional


class TaskBackendError(Exception):
    """Exception générale cockpit backend pour les tâches asynchrones."""


class TaskTimeoutError(TaskBackendError):
    def __init__(self, timeout: Optional[float] = None) -> None:
        message = (
            f"⏱️ Délai d’exécution dépassé après {timeout:.2f}s"
            if timeout is not None
            else "⏱️ Délai d’exécution dépassé"
        )
        super().__init__(message)


class TaskServerError(TaskBackendError):
    def __init__(self, detail: str = "💥 Échec d’exécution de la tâche côté serveur") -> None:
        super().__init__(detail)


class NoTaskFound(TaskBackendError):
    def __init__(self, detail: str = "🔍 Aucune tâche trouvée à exécuter") -> None:
        super().__init__(detail)
