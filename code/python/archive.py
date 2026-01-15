from datetime import datetime
from pathlib import Path
from utils import *
import json


def initLogs(original_email: str):
    """
    Initialise la structure de base des logs d’archivage pour une session de watermarking.

    Cette fonction crée un dictionnaire contenant :
    - un timestamp ISO de génération,
    - le hash de l’email original,
    - une liste globale des empreintes (hash email + hash mots porteurs),
    - un espace pour stocker les informations par employé.

    Args:
        original_email (str): Email original (texte brut) avant watermarking.

    Returns:
        tuple[dict, str]:
            - logs (dict): Dictionnaire initial des logs.
            - timestamp (str): Timestamp au format ISO (ex: "2026-01-15T12:34:56.000000").

    """

    variantes = {}
    all_variantes = []
    now = datetime.now()
    timestamp = now.isoformat()
    logs = {
        "timestamp:": f"{timestamp}",
        "original_email_hash": hash_email(original_email),
        "all variantes": all_variantes,
        "variantes": variantes
        }

    return logs, timestamp


def archive(creds: dict, original_email: str) -> dict:
    """
    Construit un dictionnaire de logs complet pour archiver les variantes watermarkées.

    La fonction utilise le template créé `initLogs` en ajoutant pour chaque employé :
    - son identifiant binaire (recalculé en fonction du nombre de mots porteurs),
    - le hash SHA-256 de l’email final (variante watermarkée),
    - le hash SHA-256 des mots porteurs (watermark carriers).

    Les hashes (email + mots porteurs) sont également ajoutés dans une liste globale `all variantes`
    afin de faciliter la recherche lors de l'identification .

    Args:
        creds (dict): Dictionnaire contenant les informations de watermarking par employé.
        original_email (str): Email original (texte brut), non modifié.

    Returns:
        dict: Dictionnaire complet prêt à être sauvegardé dans un fichier JSON.

    """
    finalLogs = {}
    init, actual = initLogs(original_email)
    finalLogs.update(init)
    for employee, [_, _, _] in creds.items():
        # Hash de l'email
        emailHash = format(hash_email(creds[employee][2]))
        # Hash des mots porteurs
        wordHash_tmp = ''.join(creds[employee][0])
        wordHash = hash_email(wordHash_tmp)

        # Création du dico type par employé
        temp_dict_employee = {
            "Employe": f"{employee}",
            "id binaire": decimalToBinary(creds[employee][1], len(creds[employee][0])),
            "hash email": emailHash,
            "word hash": wordHash

        }

        # Ajout dans le dico logs, et ajout des emails hash et word hash dans une liste pour faciliter la recherche
        finalLogs["all variantes"].append(emailHash)
        finalLogs["all variantes"].append(wordHash)
        finalLogs["variantes"][employee] = temp_dict_employee
    return finalLogs


def addArchive(finalLogs: dict) -> bool:
    """
    Sauvegarde les logs de watermarking dans un fichier JSON dans le dossier `logs/`.

    Le fichier est nommé automatiquement selon le format :
        watermark_<hash_email_original>_<nb_variantes>.json

    Si un fichier portant déjà le même nom existe, aucun écrasement n’est effectué afin de préserver les archives.

    Args:
        finalLogs (dict): Dictionnaire final contenant toutes les informations de logs

    Returns:
        bool:
            - True : si le fichier JSON a bien été écrit
            - False : si un fichier identique existe déjà (pas d’écrasement)

    """

    # Aller au dossier parent de "code" → "Canary"
    base_dir = Path(__file__).resolve().parents[2]  # Canary/
    data_path = base_dir / "logs"

    # Créer le dossier s'il n'existe pas
    data_path.mkdir(parents=True, exist_ok=True)

    filename = f"watermark_{finalLogs['original_email_hash']}_{len(finalLogs['variantes'])}.json"
    # Chercher le prochain index de fichier disponible
    if (data_path / f"{filename}").exists():
        print("⚠️ | Le fichier n'a pas été archivé car le watermarking de cet email avec le même nombre de variantes "
              "existe déjà.")
        return False

    # Écrire les logs dans le fichier suivant
    file_path = data_path / f"{filename}"
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(finalLogs, f, indent=4, ensure_ascii=False)

    print(f"✅ Logs enregistrés dans {file_path}")

    return True