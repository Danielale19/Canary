from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from archive import *
import uvicorn

from text_watermarking import *

app = FastAPI()

templates = Jinja2Templates(directory="template")

@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate_emails(
    request: Request,
    email: str = Form(...),
    nb_variantes: int = Form(...)
):
    INTER_LIST = inter_pair_list(email)
    nb_bits = len(INTER_LIST)

    if verif(INTER_LIST, nb_variantes):
        IDs_LIST = genBits(nb_variantes, nb_bits)
        print(IDs_LIST)
        print(INTER_LIST)
        creds = watermark_words(IDs_LIST, nb_variantes, INTER_LIST)
        email_liste_variantes, creds = watermark_emails(email, creds)

        resultats = [{"nom": nom, "texte": texte} for nom, texte in email_liste_variantes.items()]


        print("\n🚨— Archivage des informations")
        finalLogs = archive(creds, email)
        log_archive = addArchive(finalLogs)

        return templates.TemplateResponse("form.html", {
            "request": request,
            "email_original": email,
            "resultats": resultats,
            "log": log_archive
        })
    else:
        # Erreur si pas assez de mots porteurs
        return templates.TemplateResponse("form.html", {
            "request": request,
            "email_original": email,
            "error": f"❌ Impossible de générer {nb_variantes} variantes avec seulement {nb_bits} mots porteurs."
        })

@app.post("/identify", response_class=HTMLResponse)
async def identify_employee(
        request: Request,
        email_leak: str = Form(...),
):
    id_employee, information = logs_identify(email_leak)

    if (id_employee != False) and (information):
        nom = id_employee["Employe"]
        id_binaire = id_employee["id binaire"]
        hash_email = id_employee["hash email"]
        info = True

        return templates.TemplateResponse("form.html", {
            "request": request,
            "nom": nom,
            "id_binaire": id_binaire,
            "hash_email": hash_email,
            "info": info
        })

    elif ((id_employee != False) and (not information)):
        nom = id_employee["Employe"]
        id_binaire = id_employee["id binaire"]
        hash_email = id_employee["hash email"]
        info = False

        return templates.TemplateResponse("form.html", {
            "request": request,
            "nom": nom,
            "id_binaire": id_binaire,
            "hash_email": hash_email,
            "info": info
        })

    else:
        return templates.TemplateResponse("form.html", {
            "request": request,
            "error": f"❌ Nous n'avons pas réussi à récupérer à qui appartenait cet email.",
        })


# 💡 Pour lancer l'app localement avec: uvicorn apicode:app --reload
if __name__ == "__main__":
    uvicorn.run("apicode:app", host="127.0.0.1", port=8000, reload=True)