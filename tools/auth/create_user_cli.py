import os
import typer
import re
import json

app = typer.Typer()


def setup_django():
    """📦 Initialise Django pour accéder au modèle User"""
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        os.getenv("DJANGO_SETTINGS_MODULE", "oliplus.settings.local")
    )
    import django
    django.setup()


def is_valid_email(email: str) -> bool:
    """📬 Vérifie la validité syntaxique d’un e-mail"""
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))


@app.command("create-user")
def create_user(
    username: str = typer.Argument(..., help="Nom d’utilisateur (unique)"),
    email: str = typer.Option(..., "--email", "-e", help="Adresse e-mail"),
    poste: str = typer.Option(None, "--poste", "-p", help="Poste RH (admin, rh, etc.)"),
    password: str = typer.Option(
        None,
        "--password", "-w",
        prompt=True,
        hide_input=True,
        help="Mot de passe (sera demandé si omis)"
    ),
    is_staff: bool = typer.Option(False, "--staff", help="Attribuer les droits staff"),
    is_superuser: bool = typer.Option(False, "--superuser", help="Attribuer les droits admin"),
    force: bool = typer.Option(False, "--force", help="Remplacer l’utilisateur s’il existe"),
    json_output: bool = typer.Option(False, "--json", help="Affiche la sortie en JSON"),
):
    """👤 Crée un utilisateur Django cockpitifié"""
    setup_django()
    from django.contrib.auth import get_user_model
    from django.core.exceptions import ValidationError

    User = get_user_model()

    if not is_valid_email(email):
        typer.secho("⚠️ E-mail invalide", fg=typer.colors.YELLOW)
        raise typer.Exit(1)

    # 🔄 Suppression conditionnelle si déjà présent
    if User.objects.filter(username=username).exists():
        if force:
            User.objects.filter(username=username).delete()
            typer.secho(f"🗑️ Ancien utilisateur '{username}' supprimé", fg=typer.colors.YELLOW)
        else:
            typer.secho(f"⛔ Utilisateur '{username}' déjà existant. Utilise --force pour le recréer.", fg=typer.colors.RED)
            raise typer.Exit(1)

    # ⚙️ Construction du payload utilisateur
    fields = {
        "username": username,
        "email": email,
        "password": password,
        "is_staff": is_staff,
        "is_superuser": is_superuser,
    }

    if poste:
        if hasattr(User, "poste"):
            fields["poste"] = poste
        else:
            typer.secho("⚠️ Champ 'poste' ignoré (non défini dans User)", fg=typer.colors.YELLOW)

    try:
        user = User.objects.create_user(**fields)
        typer.secho(f"✅ Utilisateur '{user.username}' créé avec succès", fg=typer.colors.GREEN)

        # 🧾 Retour cockpit JSON ou CLI
        result = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "poste": getattr(user, "poste", None),
            "staff": user.is_staff,
            "admin": user.is_superuser
        }

        if json_output:
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.echo(f"🎓 Poste RH : {result['poste']}")
            typer.echo(f"📬 Email : {result['email']}")
            typer.echo(f"🔐 Droits : staff={result['staff']} / admin={result['admin']}")

    except ValidationError as ve:
        typer.secho(f"❌ Erreur de validation : {ve.messages}", fg=typer.colors.RED)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"❌ Erreur inattendue : {type(e).__name__} → {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
