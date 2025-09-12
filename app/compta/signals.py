import datetime
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models.facture import Facture
from .models.devis import Devis

def generate_numero(prefix: str, model_cls, include_month=False) -> str:
    """🔢 Génère un numéro unique basé sur l’année (et le mois si demandé)"""
    now = timezone.now()
    year = now.year
    month = now.month if include_month else None

    base = f"{prefix}-{year}"
    if include_month:
        base += f"-{month:02d}"

    count = model_cls.objects.filter(numero__startswith=base).count() + 1
    numero = f"{base}-{count:04d}"

    # Vérification d’unicité
    if model_cls.objects.filter(numero=numero).exists():
        raise ValidationError(f"Le numéro {numero} existe déjà.")

    return numero

def assign_numero_if_missing(instance, prefix, model_cls, include_month=False):
    """🧠 Assigne un numéro si absent"""
    if not instance.numero:
        instance.numero = generate_numero(prefix, model_cls, include_month)
    else:
        instance.numero = instance.numero.strip().upper()

@receiver(pre_save, sender=Facture)
def set_facture_numero(sender, instance: Facture, **kwargs):
    assign_numero_if_missing(instance, "F", Facture)

@receiver(pre_save, sender=Devis)
def set_devis_numero(sender, instance: Devis, **kwargs):
    assign_numero_if_missing(instance, "D", Devis)
