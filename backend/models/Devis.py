from django.db import models


class Devis(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    client = models.CharField(max_length=128)
    date_creation = models.DateField(auto_now_add=True)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    validé = models.BooleanField(default=False)
    date_validation = models.DateField(null=True, blank=True)
    service = models.CharField(max_length=128, blank=True)
    commentaire = models.TextField(blank=True, help_text="Annotation cockpit interne")

    def __str__(self):
        return f"Devis {self.numero} — {self.client}"

    class Meta:
        verbose_name = "Devis cockpitifié"
        verbose_name_plural = "Devis cockpitifiés"
        ordering = ["-date_creation"]
