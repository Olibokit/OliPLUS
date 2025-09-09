import json
import unicodedata
from pathlib import Path
from typing import Union

try:
    from rich import print
except ImportError:
    pass  # fallback to standard print if rich is not installed

PathLike = Union[str, Path]


def normalize_path(path_str: PathLike) -> Path:
    """
    Convertit un chemin brut en chemin absolu nettoyé.
    """
    return Path(path_str).expanduser().resolve()


def load_json(path: PathLike) -> dict:
    """
    Charge un fichier JSON et retourne son contenu.

    Args:
        path (PathLike): Chemin vers le fichier JSON.

    Returns:
        dict: Contenu du fichier JSON.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        ValueError: Si le JSON est invalide.
    """
    path = normalize_path(path)
    if not path.is_file():
        raise FileNotFoundError(f"[red]❌ Fichier introuvable :[/red] {path}")
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"[yellow]⚠️ JSON invalide dans '{path.name}'[/yellow] : {e.msg} (ligne {e.lineno}, colonne {e.colno})"
        )


def is_valid_json(path: PathLike) -> bool:
    """
    Vérifie si un fichier est un JSON valide.

    Args:
        path (PathLike): Chemin vers le fichier.

    Returns:
        bool: True si valide, False sinon.
    """
    path = normalize_path(path)
    if not path.is_file():
        return False
    try:
        with path.open(encoding="utf-8") as f:
            json.load(f)
        return True
    except json.JSONDecodeError:
        return False


def slugify(value: str, separator: str = "-") -> str:
    """
    Transforme une chaîne en identifiant lisible.

    Args:
        value (str): Texte à transformer.
        separator (str): Caractère de séparation.

    Returns:
        str: Slug généré.
    """
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().replace(" ", separator).replace("_", separator)
    return value.strip(separator)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="🧰 Outils JSON & Slugify")
    parser.add_argument("action", choices=["load", "check", "slug"], help="Action à effectuer")
    parser.add_argument("input", help="Chemin du fichier ou texte à traiter")
    args = parser.parse_args()

    if args.action == "load":
        try:
            data = load_json(args.input)
            print("[green]✅ JSON chargé avec succès :[/green]")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(e)

    elif args.action == "check":
        if is_valid_json(args.input):
            print("[green]✅ JSON valide[/green]")
        else:
            print("[red]❌ JSON invalide ou fichier introuvable[/red]")

    elif args.action == "slug":
        print(f"[blue]🔤 Slug :[/blue] {slugify(args.input)}")


if __name__ == "__main__":
    main()
