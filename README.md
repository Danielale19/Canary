# Canary — Watermarking d’emails & attribution de fuite

Canary est un **Proof of Concept** permettant de générer **plusieurs variantes uniques** d’un même email (via des substitutions contrôlées de synonymes) afin d’ajouter une **empreinte invisible** par destinataire.  
En cas de fuite, l’outil peut ensuite **retrouver à qui la version fuité a été envoyée** en comparant l’email à des logs archivés sous forme de **hashs**.

> 🛠️ **Projet en cours** : Canary est encore en développement. Certaines fonctionnalités et optimisations sont prévues dans les prochaines versions.

---

## ✅ Fonctionnalités

- Génération de **N variantes watermarkées** à partir d’un email source
- Watermarking via **mots porteurs** (synonymes)
- Attribution d’une **signature binaire** (empreinte) par destinataire
- Archivage des variantes via **hash SHA-256** (pas de stockage d’emails en clair dans les logs)
- Détection / attribution : identification du destinataire à partir d’un email fuité
- Interface web minimaliste avec **FastAPI + Jinja2**

---

## 🧠 Principe de fonctionnement

1. L’email est analysé pour détecter des **mots porteurs** (mots présents dans une liste de synonymes).
2. Chaque mot porteur correspond à une **position binaire**.
3. Pour chaque employé, un identifiant binaire est généré :
   - `0` → mot conservé
   - `1` → mot remplacé par son synonyme
4. Les variantes sont générées puis archivées dans `logs/` sous forme d’empreintes.

📌 **Capacité :** si l’email contient `k` mots porteurs, on peut créer jusqu’à :

2^k >= nombre de variantes

---

## 🧱 Stack technique

- **Python 3**
- **FastAPI**
- **Uvicorn**
- Stockage JSON (logs) + **SHA-256 hashing**

---

## 📁 Structure du projet

```bash
Canary/
├─ code/python/
│  ├─ apicode.py              # Application FastAPI (routes + UI)
│  ├─ text_watermarking.py    # Logique de watermarking
│  ├─ archive.py              # Archivage + écriture des logs
│  ├─ utils.py                # Helpers (hash, binaire, etc.)
│  └─ template/form.html      # Interface HTML
├─ data/                      # Dictionnaires de synonymes (FR)
├─ logs/                      # Archives JSON générées (peut être ignoré en Git)
├─ README.md
└─ requirements.txt
```

## 🚀 Installation

### 1) Prérequis
- Python **3.10+** recommandé  
- `pip`

### 2) Installation

```bash
git clone https://github.com/Danielale19/Canary.git
cd Canary

pip install -r requirements.txt
```

## ▶️ Lancer l’application

⚠️ Il faut lancer le serveur depuis code/python.

```bash
cd code/python
uvicorn apicode:app --reload
```

Puis ouvrir :
- http://127.0.0.1:8000

## 🧪 Utilisation

### ✅ Générer des variantes
- Coller un email original
- Choisir le nombre de variantes
- Cliquer sur Générer
- Canary affiche les variantes et archive les empreintes dans logs/

### 🔎 Identifier une fuite

- Coller l’email suspect (leak)
- Cliquer sur Identifier
- Canary renvoie le destinataire le plus probable (match fort ou match partiel)



## 🗃️ Logs & archivage

Les logs sont enregistrés dans logs/ au format :

```bash
watermark_<hash_email_original>_<nb_variantes>.json
```

Chaque fichier contient :
- original_email_hash : hash de l’email d’origine
- all variantes : liste des empreintes (hash email + hash mots porteurs)
- variantes : détails par employé (id binaire, hashes, etc.)


🔧 Améliorations prévues

- Stockage à l'aide d'un BDD (SQLite / PostgreSQL)
- Tokenisation plus fiable (modifier le système de watermarking avec plus de mots watermarké / emails)
- Amélioration de l’identification (mettre en place un système plus avancé et créer une empreinte numérique pour chaque email)
- Améliorer la partie Web

✍️ Auteur

Daniel — GitHub : @Danielale19
