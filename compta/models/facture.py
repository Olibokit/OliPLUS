from django.db import models
from django.utils import timezone
from .devis import Devis

class Facture(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoyée', 'Envoyée'),
        ('payée', 'Payée'),
    ]

    numero = models.CharField(max_length=20, unique=True)
    devis_source = models.ForeignKey(Devis, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.CharField(max_length=128)
    date_emission = models.DateField(auto_now_add=True)
    date_echeance = models.DateField()
    date_paiement = models.DateField(null=True, blank=True)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=32, choices=STATUT_CHOICES, default='brouillon')
    reference_externe = models.CharField(max_length=64, blank=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_emission']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return f"🧾 Facture {self.numero} — {self.client}"

    def is_overdue(self):
        return self.statut != 'payée' and self.date_echeance < timezone.now().date()

    def clean(self):
        # 🧠 Validation logique : si payée, date_paiement requise
        if self.statut == 'payée' and not self.date_paiement:
            raise ValidationError("La date de paiement est requise pour une facture marquée comme payée.")

    def save(self, *args, **kwargs):
        self.commentaire = self.commentaire.strip()
        super().save(*args, **kwargs)
