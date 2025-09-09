from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional


class TaskBackend(ABC):
    """
    Interface cockpit pour les backends d'exécution de tâches.

    Chaque backend doit implémenter la méthode `submit`, qui permet
    d'envoyer une tâche typée avec son payload et ses métadonnées optionnelles.

    Exemple d'implémentation :
        class KafkaBackend(TaskBackend):
            def submit(self, task: str, payload: Mapping[str, Any], metadata: Optional[Mapping[str, Any]] = None) -> Any:
                # Envoi cockpitifié via Kafka
                ...

    """

    @abstractmethod
    def submit(
        self,
        task: str,
        payload: Mapping[str, Any],
        metadata: Optional[Mapping[str, Any]] = None
    ) -> Any:
        """
        Soumet une tâche cockpitifiée à un backend d'exécution.

        :param task: Nom ou identifiant de la tâche
        :param payload: Données associées à la tâche
        :param metadata: Métadonnées optionnelles (trace, audit, contexte)
        :return: Résultat ou identifiant de soumission
        """
        pass
