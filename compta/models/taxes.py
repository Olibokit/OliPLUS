from django.db import models

class Pays(models.Model):
    nom = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.nom.title()


class Taxe(models.Model):
    TYPES_TAXE = [
        ("TVA", "Taxe sur la valeur ajoutée"),
        ("DOUANE", "Taxe douanière"),
        ("ECO", "Écocontribution"),
        ("AUTRE", "Autre taxe"),
    ]

    nom = models.CharField(max_length=64, unique=True)
    taux = models.DecimalField(max_digits=5, decimal_places=2)  # ex: 20.00
    type = models.CharField(max_length=16, choices=TYPES_TAXE, default="AUTRE")
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name="taxes")
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Taxe"
        verbose_name_plural = "Taxes"
        ordering = ["nom"]
        indexes = [
            models.Index(fields=["nom"]),
        ]

    def clean(self):
        if self.taux < 0 or self.taux > 100:
            raise ValueError("Le taux doit être entre 0% et 100%.")

    def __str__(self):
        return f"{self.nom.title()} – {self.taux}% ({self.get_type_display()})"
