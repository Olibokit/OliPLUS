#!/usr/bin/env python
import os
import sys
import typer
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from OliPLUS.OliPLUS.oliplus_toolchain.models.orm import Base

app = typer.Typer(help="🧱 Initialisation ou réinitialisation de la base cockpit")

@app.command()
def init(
    reset: bool = typer.Option(False, "--reset", help="❗ Supprime les tables existantes avant création"),
    env_file: str = typer.Option(".env", "--env-file", help="📄 Fichier .env à charger")
):
    # 🔧 Chargement de l’environnement
    if not os.path.exists(env_file):
        typer.secho(f"❌ Fichier .env introuvable : {env_file}", fg=typer.colors.RED)
        raise typer.Exit(1)

    load_dotenv(env_file)
    typer.secho(f"📄 Environnement chargé depuis : {env_file}", fg=typer.colors.BLUE)

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        typer.secho("❌ DATABASE_URL introuvable dans .env", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.secho(f"🔗 Connexion à la base : {db_url}", fg=typer.colors.CYAN)
    engine = create_engine(db_url)

    if reset:
        typer.secho("⚠️ Réinitialisation demandée", fg=typer.colors.YELLOW)
        confirm = typer.confirm("Cette opération va supprimer toutes les tables. Continuer ?", abort=True)
        Base.metadata.drop_all(bind=engine)
        typer.secho("🗑️ Tables supprimées", fg=typer.colors.YELLOW)

    Base.metadata.create_all(bind=engine)
    typer.secho("✅ Tables créées avec succès", fg=typer.colors.GREEN)

    # 📘 Liste des tables
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result]
        typer.echo("\n📂 Tables actuelles :")
        for table in tables:
            typer.echo(f"  • {table}")
        typer.echo(f"\n📊 Total : {len(tables)} table(s)")

if __name__ == "__main__":
    app()
