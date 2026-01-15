from pathlib import Path
from utils import *
import json


def json_file(filename: str) -> dict:
    """
    Charge et retourne un fichier JSON depuis le dossier `data/` du projet.

    Args:
        filename (str): Nom du fichier JSON à charger (ex: "synonymes_fr_dict.json").

    Returns:
        dict: Contenu du fichier JSON chargé sous forme de dictionnaire Python.

    """
    # Aller au dossier parent de "code" → "Canary"
    base_dir = Path(__file__).resolve().parents[2]  # Canary/
    data_path = base_dir / "data" / filename
    with data_path.open(encoding="utf-8") as f:
        return json.load(f)


# Exemple d’utilisation :
PAIR_LIST = json_file("synonymes_fr_dict.json")
PAIR_LIST_BRUT = json_file("synonymes_fr_words.json")


def read_email(email: str) -> list[str]:
    """
    Nettoie un email et le transforme en liste de mots (tokenisation simple).

    Args:
        email (str): Texte brut de l’email à traiter.

    Returns:
        list[str]: Liste des mots extraits de l’email après nettoyage.
    """

    texte = email.lower()
    ponctuation = ".,!?;:()\"«»-\n"
    for word in ponctuation:
        texte = texte.replace(word, " ")
    email_list = texte.split()
    return email_list


def inter_pair_list(text_email: str) -> list[str]:
    """
    Extrait la liste des mots porteurs (mots pour lesquels on a un synonyme) présents dans un email.

    Args:
        text_email (str): Contenu de l’email (texte brut).

    Returns:
        list[str]: Liste ordonnée des mots porteurs présents dans l’email.
    """

    EMAIL_LIST = read_email(text_email)
    word_inter = []
    for word in EMAIL_LIST:
        if word in PAIR_LIST_BRUT:
            word_inter.append(word)
    return word_inter


def verif(inter_list, nb_variantes):
    return 2 ** len(inter_list) >= nb_variantes


def watermark_words(IDs_LIST : dict, nb_variantes : int, INTER_LIST : dict):
    """
    Construit la "signature watermark" de chaque destinataire en appliquant un identifiant binaire
    sur une liste de mots porteurs (carrier words).

    Pour chaque employé, la fonction :
    - associe un identifiant binaire (ex: "0101...") provenant de `IDs_LIST`,
    - parcourt chaque bit et remplace le mot porteur correspondant par son synonyme si le bit vaut "1",
    - conserve le mot original si le bit vaut "0",
    - retourne un dictionnaire contenant, pour chaque employé :
        • la liste finale des mots porteurs codés (EDIT_LIST)
        • l’identifiant en décimal associé à l’ID binaire

    Args:
        IDs_LIST (list[str]):
            Liste des identifiants binaires à attribuer aux employés.
            Exemple : ["0001", "0010", "0011", ...]
        nb_variantes (int):
            Nombre de variantes à générer.
            Doit être <= len(IDs_LIST).
        INTER_LIST (list[str]):
            Liste des mots porteurs détectés dans l’email original, dans l’ordre.
            Chaque mot doit exister dans `PAIR_LIST` (en clé ou en valeur).

    Returns:
        dict:
            Dictionnaire structuré par employé, au format :
            {
                "Employé 1": [EDIT_LIST, id_decimal],
                "Employé 2": [EDIT_LIST, id_decimal],
                ...
            }
            où :
            - EDIT_LIST (list[str]) : liste des mots porteurs après watermarking (synonymes appliqués selon l'ID)
            - id_decimal (int) : version décimale de l'ID binaire
    """

    CREDS = {}
    nb_bits = len(INTER_LIST)
    for i in range(0, nb_variantes):
        CREDS[f"Employé {i + 1}"] = IDs_LIST[i]
    for worker, id in CREDS.items():
        EDIT_LIST = INTER_LIST.copy()
        for i in range(0, nb_bits):
            # Cas de figure où on doit remplacer le mot par un synonyme
            if id[i] == "1":
                try:
                    # Si le synonyme est la value du dico
                    EDIT_LIST[i] = PAIR_LIST[INTER_LIST[i]]
                except:
                    # Si le synonyme se trouve en key du dico
                    EDIT_LIST[i] = PAIR_LIST[get_key_from_value(PAIR_LIST, INTER_LIST[i])]
            else:
                # Cas où on ne doit pas remplacer le mot par un synonyme
                EDIT_LIST[i] = INTER_LIST[i]
        # Mis à jour du dico creds qui contient toutes les infos (codes binaire etc...)
        CREDS[worker] = [EDIT_LIST, binaryToDecimal(id)]
    return CREDS


def watermark_emails(email: str, creds: dict):
    """
    Génère des variantes watermarkées d’un email en appliquant les remplacements
    de mots porteurs calculés précédemment pour chaque destinataire.

    Cette fonction :
    - détecte les mots porteurs présents dans l’email (`inter_pair_list`),
    - applique, pour chaque employé, les substitutions prévues dans `creds`,
    - construit un dictionnaire {Employé: email_modifié},
    - ajoute également le texte final de l’email modifié dans `creds`.

    Args:
        email (str): Texte de l’email original (non watermarké).
        creds (dict): Données de watermarking par destinataire, généralement produites par
            `watermark_words()`. Le format attendu est proche de :
            {
                "Employé 1": [mots_codes, ...],
                "Employé 2": [mots_codes, ...],
                ...
            }
            où `mots_codes` est une liste de mots (codes/synonymes) correspondant aux mots porteurs.

    Returns:
        tuple[dict, dict]:
            - resultat (dict): Dictionnaire contenant les emails finalisés par employé :
              { "Employé X": "email_modifié", ... }
            - creds (dict): Même structure que l’entrée, enrichie avec l’email final de chaque employé
              (ajout en fin de liste via `append()`).
    """
    inter_list = inter_pair_list(email)
    email_base = email
    resultat = {}

    for employe, (mots_codes, _) in creds.items():
        email_modifie = email_base
        for mot_original, mot_code in zip(inter_list, mots_codes):
            if mot_original != mot_code:
                email_modifie = email_modifie.replace(mot_original, mot_code)
        resultat[employe] = email_modifie
        creds[employe].append(resultat[employe])

    return resultat, creds



def logs_identify(email: str):
    """
    Identifie le destinataire d’un email (potentiellement fuité) en comparant son empreinte aux archives disponibles dans le dossier `logs/`.

    La fonction calcule :
    - le hash SHA-256 de l’email complet,
    - le hash SHA-256 des mots porteurs (watermarked words),
    puis parcourt les fichiers JSON archivés afin de retrouver une correspondance.

    Deux niveaux de certitude sont renvoyés :
    - ✅ Match sur le hash de l’email complet → identification certaine (100%)
    - ⚠️ Match sur le hash des mots porteurs → identification probable (quasi certaine)

    Args:
        email (str): Contenu de l’email à analyser (texte brut).

    Returns:
        tuple[dict | bool, bool]:
            - info (dict | False): Dictionnaire contenant les informations du destinataire
              (ex: identifiant binaire, hash, etc.), ou False si aucune correspondance trouvée.
            - bool (bool): Indicateur de fiabilité :
                * True  -> correspondance exacte sur l'email hash (100%)
                * False -> correspondance sur le hash des mots porteurs uniquement (certitude partielle)
                  ou aucune correspondance (retourne False, False)

    """

    # Hash de l'email en question
    email_hash = hash_email(email)
    # Hash des mots porteurs
    importantWord = inter_pair_list(email)
    wordHash = hash_email(''.join(importantWord))
    # Aller directement au fichier logs
    base_dir = Path(__file__).resolve().parents[2]  # Canary/
    dossier_path = base_dir / "logs"

    # Cas error
    if not dossier_path.exists():
        print(f"❌ — Erreur, impossible d'accéder aux logs.")
        return False, False

    # Lecture de tout les fichiers
    for fichier in dossier_path.glob("*.json"):
        print(f"📂 Lecture du fichier : {fichier.name}")

        with open(fichier, "r", encoding="utf-8") as f:
            contenu = json.load(f)

            # Si l'on trouve le hash de l'email ou le hash des mots porteurs, on arrête la recherche
            if (email_hash in contenu["all variantes"]) or (wordHash in contenu["all variantes"]):
                print("✅ — Fichier logs trouvé !")
                break

    cible = contenu["variantes"]
    for employee, info in cible.items():
        # Si l'on a trouvé le hash de l'email, on stop et renvoie les infos sur l'employé + True pour dire qu'on est
        # sûr à 100 %
        if info["hash email"] == email_hash:
            print("✅ — Employé trouvé ! Test email succès")
            return info, True
        else:
            # Idem, mais pour les mots porteurs, donc potentiellement sûr
            if info["word hash"] == wordHash:
                print("✅ — Employé trouvé ! Test mots porteur succès")
                return info, False
    # Cas où rien a été trouvé
    return False, False