from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class SearchFilter(BaseModel):
    """
    🔍 Recherche texte globale, optionnelle (sSearch cockpit).
    """
    search: Optional[str] = Field(
        default=None,
        example="durand",
        description="Texte à rechercher globalement (nom, email, etc.)"
    )

class PaginationParams(BaseModel):
    """
    📄 Paramètres standardisés pour la pagination cockpit.
    """
    page: int = Field(
        default=1,
        ge=1,
        description="Numéro de page (≥ 1)"
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Nombre d'éléments par page (1 à 100)"
    )

class OrderBy(BaseModel):
    """
    ↕️ Ordre de tri sur un champ donné.
    """
    field: str = Field(
        ...,
        description="Nom du champ à trier (ex: 'last_name')"
    )
    direction: Literal["asc", "desc"] = Field(
        default="asc",
        description="Direction du tri : 'asc' ou 'desc'"
    )

class EmployeeFilters(SearchFilter, PaginationParams):
    """
    🧑‍💼 Filtres spécifiques pour la liste des employés.
    """
    department_id: Optional[int] = Field(
        default=None,
        description="ID du département pour filtrer"
    )
    status: Optional[str] = Field(
        default=None,
        example="Active",
        description="Statut de l'employé (ex: 'Active', 'Inactive')"
    )
    order_by: Optional[List[OrderBy]] = Field(
        default=None,
        description="Liste des critères de tri"
    )
    show_subordinates_only: bool = Field(
        default=False,
        description="Afficher uniquement les subordonnés de l'utilisateur courant"
    )
