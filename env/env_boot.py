from env.loader import load_environment
from env.checks import run_checks
from env.summary import print_summary
import sys

def main():
    print("🛩️ Initialisation du cockpit environnemental...\n")

    try:
        env_file = load_environment()
        errors, warnings = run_checks()
        print_summary(env_file, errors, warnings)

        if errors:
            print("\n❌ Erreurs critiques détectées. Démarrage interrompu.")
            sys.exit(1)
        else:
            print("\n✅ Environnement prêt. Lancement possible.")
    except Exception as e:
        print(f"\n🔥 Exception inattendue : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
