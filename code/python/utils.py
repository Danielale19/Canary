import hashlib


### Fonction de hash (email)
def hash_email(email_text: str) -> str:
    """
    Retourne le hash SHA-256 d’un email texte.
    """
    return hashlib.sha256(email_text.encode('utf-8')).hexdigest()


### Fonction de conversion binaire
def decimalToBinary(n, bits):
    if n < 0 or n >= 2**bits:
        raise ValueError(f"Le nombre {n} ne peut pas être représenté sur {bits} bits.")
    binaire = ""
    while n > 0:
        binaire = str(n % 2) + binaire
        n = n // 2
    return binaire.zfill(bits)

def genBits(nb_variantes, nb_bits):
    list_id = []
    for i in range(0,nb_variantes):
        list_id.append(decimalToBinary(i,nb_bits))
    return list_id

def binaryToDecimal(binaire):
    # Vérifie que l'entrée est bien une chaîne de 0 et 1
    if not all(bit in '01' for bit in binaire):
        raise ValueError("La chaîne doit contenir uniquement des 0 et des 1.")

    decimal = 0
    puissance = len(binaire) - 1

    for bit in binaire:
        decimal += int(bit) * (2 ** puissance)
        puissance -= 1

    return decimal


def get_key_from_value(dico, valeur_recherchee):
    for cle, valeur in dico.items():
        if valeur == valeur_recherchee:
            return cle
    return None  # ou raise une exception si tu veux


def format(text):
    texte = text.lower()
    ponctuation = ".,!?;:()\"«»-\n "
    res=""
    for word in ponctuation:
        texte = texte.replace(word, "")
    return(texte)