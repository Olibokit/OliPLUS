from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "display_or_dash_full_name",
        "colored_poste",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_display_links = ("username", "email")
    list_filter = ("poste", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name", "poste")
    ordering = ("last_name", "first_name")
    readonly_fields = ("last_login", "date_joined")
    autocomplete_fields = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Infos personnelles", {"fields": ("first_name", "last_name", "poste")}),
        (
            "Permissions cockpit",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Journalisation", {"fields": ("last_login", "date_joined")}),
    )

    def display_or_dash_full_name(self, obj):
        full_name = obj.get_full_name()
        return full_name if full_name else "—"
    display_or_dash_full_name.short_description = "Nom complet"

    def colored_poste(self, obj):
        color_map = {
            "admin": "#2563eb",         # bleu
            "etudiant": "#4b5563",      # gris
            "compta": "#f59e0b",        # jaune
            "auteur": "#10b981",        # vert
            "illustrateur": "#ec4899",  # rose
            "rh": "#8b5cf6",            # violet
            "archiviste": "#ef4444",    # rouge
        }
        poste_display = obj.get_poste_display() or "—"
        color = color_map.get(obj.poste, "#6b7280")  # gris par défaut
        return format_html(
            '<span style="padding:2px 8px; border-radius:12px; background:{}; color:white;">{}</span>',
            color,
            poste_display,
        )
    colored_poste.short_description = "Poste"
