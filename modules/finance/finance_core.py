# 📦 finance_core.py — Moteur cockpitifié des opérations financières

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from models.facture import Facture
from models.devis import Devis
from models.paiement import Paiement

class FinanceCore:
    """
    Moteur cockpitifié pour la gestion des opérations financières :
    devis, factures, paiements, échéances, validation.
    """

    def __init__(self):
        self.devis_list: List[Devis] = []
        self.factures_list: List[Facture] = []
        self.paiements_list: List[Paiement] = []

    def enregistrer_devis(self, devis: Devis):
        self.devis_list.append(devis)

    def enregistrer_facture(self, facture: Facture):
        self.factures_list.append(facture)

    def enregistrer_paiement(self, paiement: Paiement):
        self.paiements_list.append(paiement)

    def calculer_total_factures(self) -> Decimal:
        return sum(f.montant for f in self.factures_list)

    def calculer_total_impayé(self) -> Decimal:
        return sum(f.montant for f in self.factures_list if not f.est_payée())

    def verifier_echeances(self) -> List[Facture]:
        aujourd_hui = datetime.today().date()
        return [f for f in self.factures_list if f.date_echeance < aujourd_hui and not f.est_payée()]

    def valider_cohérence(self) -> bool:
        """
        Vérifie que chaque paiement est bien rattaché à une facture existante.
        """
        facture_ids = {f.id for f in self.factures_list}
        return all(p.facture_id in facture_ids for p in self.paiements_list)

    def generer_rapport_financier(self) -> dict:
        return {
            "total_factures": float(self.calculer_total_factures()),
            "total_impayé": float(self.calculer_total_impayé()),
            "factures_en_retard": len(self.verifier_echeances()),
            "cohérence_validée": self.valider_cohérence()
        }
