from django.core import management
from django.utils.translation import gettext_lazy as _
from pathlib import Path

from ...classes import PythonDependency


class Command(management.BaseCommand):
    help = '📦 Génère les fichiers de dépendances Python pour un environnement donné.'

    VALID_EXTENSIONS = {'.txt', '.in'}

    def add_arguments(self, parser):
        parser.add_argument(
            'environment',
            nargs='?',
            help=_('Nom de l’environnement à cibler (ex: dev, prod)')
        )
        parser.add_argument(
            '--exclude',
            dest='exclude',
            help=_('Liste de dépendances à exclure (séparées par des virgules)')
        )
        parser.add_argument(
            '--only',
            dest='only',
            help=_('Liste de dépendances à inclure exclusivement (séparées par des virgules)')
        )
        parser.add_argument(
            '--output',
            dest='output',
            help=_('Chemin du fichier de sortie (.txt ou .in). Si omis, affiche dans la console.')
        )

    def handle(self, *args, **options):
        env = options.get('environment')
        exclude_list = self._parse_list(options.get('exclude'))
        only_list = self._parse_list(options.get('only'))
        output_path = options.get('output')

        # 🔍 Récupération des dépendances
        dependencies = PythonDependency.get_for_attribute(
            attribute_name='environments.name',
            attribute_value=env,
            subclass_only=True
        )

        if not dependencies:
            self.stderr.write(self.style.WARNING("⚠️ Aucune dépendance trouvée pour cet environnement."))
            return

        # 🧹 Filtrage
        filtered = self._filter_dependencies(dependencies, exclude_list, only_list)

        # 📤 Sortie
        if output_path:
            ext = Path(output_path).suffix
            if ext not in self.VALID_EXTENSIONS:
                self.stderr.write(self.style.ERROR("❌ Format de sortie non supporté. Utilisez .txt ou .in"))
                return

            Path(output_path).write_text('\n'.join(filtered), encoding='utf-8')
            self.stdout.write(self.style.SUCCESS(f"✅ Fichier de dépendances généré : {output_path}"))
        else:
            self.stdout.write("📋 Dépendances générées :\n")
            for line in filtered:
                self.stdout.write(f"  - {line}")
            self.stdout.write(self.style.SUCCESS(f"\n✅ Total : {len(filtered)} dépendance(s) listée(s)"))

    def _parse_list(self, raw):
        return [x.strip() for x in (raw or '').split(',') if x.strip()]

    def _filter_dependencies(self, dependencies, exclude_list, only_list):
        result = []
        for dep in dependencies:
            if only_list and dep.name not in only_list:
                continue
            if dep.name in exclude_list:
                continue

            version = dep.version_string
            if version and not version.startswith('=='):
                version = f'=={version}'
            result.append(f"{dep.name}{version or ''}")
        return result
