from __future__ import annotations
from text_watermarking import *
from archive import *
import textwrap


def _print_title(title: str) -> None:
    line = "═" * 72
    print(f"\n{line}\n{title}\n{line}")


def _print_section(title: str) -> None:
    print(f"\n── {title}")


def _pretty_email(email: str, width: int = 90) -> str:
    """
    Rend l'email plus lisible dans la console (retours à la ligne propres).
    """
    email = email.strip().replace("\n", " ")
    return textwrap.fill(email, width=width)


def main(nb_variantes: int = 10, leaked_employee: str = "Employé 2") -> int:
    """
    Main de démonstration (test manuel) :
    - Génère des variantes watermarkées
    - Archive les empreintes
    - Simule une fuite et identifie le destinataire

    Retourne 0 si OK, 1 si erreur.
    """
    _print_title("CANARY — Main de test (Watermarking & Attribution de fuite)")

    email = (
        "Bonjour, C’est important que nous puissions commencer rapidement cette tâche afin d’obtenir un bon résultat. "
        "J’ai besoin de ton aide pour tester une idée que nous pourrons ensuite changer si nécessaire. "
        "Peux-tu me montrer comment utiliser les outils dès demain ? "
        "Cela devrait permettre de créer un meilleur processus. "
        "Merci d’avance pour ton retour. Bien à toi, [Votre Nom]"
    )

    _print_section("📨 Email utilisé pour le test")
    print(_pretty_email(email))

    _print_section("⚙️ Préparation watermarking")
    inter_list = inter_pair_list(email)
    nb_bits = len(inter_list)
    capacity = 2 ** nb_bits if nb_bits > 0 else 0

    print(f"• Mots porteurs détectés : {nb_bits}")
    print(f"• Capacité maximale théorique : {capacity} variantes")

    if nb_bits == 0:
        print("\n❌ Aucun mot porteur détecté : impossible de générer des variantes.")
        return 1

    # Si l'utilisateur demande trop de variantes, on ajuste proprement
    if nb_variantes > capacity:
        print(f"\n⚠️ Demande de {nb_variantes} variantes > capacité ({capacity}).")
        nb_variantes = capacity
        print(f"➡️ Ajustement automatique : nb_variantes = {nb_variantes}")

    if not verif(inter_list, nb_variantes):
        print(
            f"\n❌ Impossible de générer {nb_variantes} variantes avec seulement {nb_bits} mots porteurs."
        )
        return 1

    try:
        _print_section("🧬 Génération des identifiants binaires")
        ids_list = genBits(nb_variantes, nb_bits)

        _print_section("🔏 Application du watermark (mots porteurs)")
        creds = watermark_words(ids_list, nb_variantes, inter_list)

        _print_section(f"📩 Génération des {nb_variantes} variantes d’emails")
        email_variantes, creds = watermark_emails(email, creds)

        # Affichage propre des variantes
        for employee, variant_text in email_variantes.items():
            print(f"\n✅ {employee}")
            print(_pretty_email(variant_text))

        _print_section("📦 Archivage (hashs + metadata)")
        final_logs = archive(creds, email)
        addArchive(final_logs)
        print("✅ Archivage terminé.")

        _print_section("🚨 Simulation de fuite + identification")

        print(f"On simule une fuite depuis : {leaked_employee}\n")
        leaked_email = email_variantes[leaked_employee]

        id_employee, information = logs_identify(leaked_email)

        print("\n📌 Résultat de l’analyse :")
        if id_employee is False:
            print("❌ Aucun propriétaire identifié (aucune correspondance forte).")
        elif information is False:
            print(f"⚠️ Correspondance partielle via mots porteurs : {id_employee.get('Employe')}")
        else:
            print(f"✅ Propriétaire identifié : {id_employee.get('Employe')}")

        print("\n🟢 Fin du test — OK")

        return 0

    except Exception as exc:
        print("\n❌ Une erreur est survenue pendant l'exécution du main de test.")
        print(f"Détails : {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

