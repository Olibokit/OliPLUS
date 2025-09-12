import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    UniteArchivistique, Contrat, Mandat, Document, Projet,
    Fournisseur, ContratEdition, ContratServiceIndependant, Royalties
)

# 🔧 Actions cockpitifiées pour Royalties
def marquer_comme_payees(modeladmin, request, queryset):
    updated = 0
    for royalty in queryset:
        if royalty.statut_paiement != "payé":
            royalty.statut_paiement = "payé"
            royalty.date_versement = timezone.now().date()
            royalty.save()
            updated += 1
    modeladmin.message_user(request, f"{updated} redevance(s) marquée(s) comme payées.")

marquer_comme_payees.short_description = "✅ Marquer comme payées"

def exporter_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=redevances_export.csv"

    writer = csv.writer(response)
    writer.writerow([
        "Auteur", "Livre", "Format", "Pourcentage", "Montant dû",
        "Statut", "Date versement", "Date effet"
    ])
    for r in queryset:
        writer.writerow([
            r.auteur.nom,
            r.livre.titre,
            getattr(r.format, "format_type", str(r.format)),
            f"{r.pourcentage:.2f}%",
            f"{r.montant_du:.2f}",
            r.get_statut_paiement_display(),
            r.date_versement or "",
            r.date_effet.strftime("%Y-%m-%d"),
        ])
    return response

exporter_csv.short_description = "📤 Exporter en CSV"

# 🧩 Admins cockpitifiés
@admin.register(UniteArchivistique)
class UniteArchivistiqueAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'statut_conservation', 'type_document',
        'niveau_acces', 'date_creation', 'date_derniere_action',
    )
    list_display_links = ('titre',)
    readonly_fields = ('date_creation', 'date_derniere_action')
    search_fields = ('titre', 'description', 'reference', 'justification_action')
    list_filter = ('statut_conservation', 'type_document', 'niveau_acces', 'date_creation')
    list_per_page = 30
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    fieldsets = (
        ("📄 Métadonnées", {
            'fields': (
                'titre', 'description', 'reference', 'type_document',
                'niveau_acces', 'statut_conservation',
                'periode_conservation_active_annee', 'periode_conservation_passive_annee',
                'justification_action', 'commentaire', 'notes',
                'date_creation', 'date_derniere_action',
            )
        }),
        ("🔗 Relations documentaires", {
            'classes': ('collapse',),
            'fields': ('contrats', 'mandats', 'documents', 'projets', 'fournisseurs')
        }),
    )
    filter_horizontal = ('contrats', 'mandats', 'documents', 'projets', 'fournisseurs')


@admin.register(Contrat)
class ContratAdmin(admin.ModelAdmin):
    list_display = ('numero_contrat', 'partie1', 'partie2', 'date_signature', 'statut')
    list_display_links = ('numero_contrat',)
    search_fields = ('numero_contrat', 'partie1__nom', 'partie2__nom')
    list_filter = ('statut', 'date_signature')
    date_hierarchy = 'date_signature'
    ordering = ('-date_signature',)
    list_select_related = ('partie1', 'partie2')


@admin.register(Mandat)
class MandatAdmin(admin.ModelAdmin):
    list_display = ('numero_mandat', 'client', 'projet', 'date_debut', 'date_fin')
    list_display_links = ('numero_mandat',)
    search_fields = ('numero_mandat', 'client__nom', 'projet__nom')
    list_filter = ('date_debut', 'date_fin')
    date_hierarchy = 'date_debut'
    ordering = ('-date_debut',)
    list_select_related = ('client', 'projet')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_document', 'taille_ko', 'date_telechargement')
    list_display_links = ('titre',)
    search_fields = ('titre', 'description')
    list_filter = ('type_document', 'date_telechargement')
    date_hierarchy = 'date_telechargement'
    ordering = ('-date_telechargement',)
    list_per_page = 25


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom_projet', 'statut', 'date_debut', 'date_fin')
    list_display_links = ('nom_projet',)
    search_fields = ('nom_projet', 'description')
    list_filter = ('statut', 'date_debut', 'date_fin')
    ordering = ('-date_debut',)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom_fournisseur', 'contact_principal', 'telephone')
    list_display_links = ('nom_fournisseur',)
    search_fields = ('nom_fournisseur', 'contact_principal')
    ordering = ('nom_fournisseur',)


@admin.register(ContratEdition)
class ContratEditionAdmin(admin.ModelAdmin):
    list_display = (
        'numero_contrat', 'ouvrage', 'date_signature',
        'fichier_pdf_tag', 'created_at', 'updated_at'
    )
    list_display_links = ('numero_contrat',)
    readonly_fields = ('fichier_pdf_tag', 'created_at', 'updated_at')
    search_fields = ('numero_contrat', 'ouvrage__titre')
    list_filter = ('date_signature',)
    date_hierarchy = 'date_signature'
    ordering = ('-date_signature',)
    list_select_related = ('ouvrage',)


@admin.register(ContratServiceIndependant)
class ContratServiceIndependantAdmin(admin.ModelAdmin):
    list_display = (
        'numero_contrat', 'prestataire', 'service',
        'date_signature', 'montant_ht', 'fichier_pdf_tag'
    )
    list_display_links = ('numero_contrat',)
    readonly_fields = ('fichier_pdf_tag', 'created_at', 'updated_at')
    search_fields = ('numero_contrat', 'prestataire__nom', 'service')
    list_filter = ('date_signature', 'service')
    date_hierarchy = 'date_signature'
    ordering = ('-date_signature',)
    list_select_related = ('prestataire',)


@admin.register(Royalties)
class RoyaltiesAdmin(admin.ModelAdmin):
    list_display = (
        "auteur", "livre", "format", "pourcentage", "montant_du",
        "statut_paiement", "date_versement", "date_effet",
    )
    list_display_links = ("livre",)
    list_filter = ("statut_paiement", "format", "date_effet", "date_versement")
    search_fields = ("auteur__nom", "livre__titre", "format__format_type")
    readonly_fields = ("montant_du", "historique_paiements", "date_versement")
    date_hierarchy = "date_effet"
    ordering = ("-date_effet",)
    list_select_related = ("auteur", "livre", "format")
    list_per_page = 50
    actions = [marquer_comme_payees, exporter_csv]
