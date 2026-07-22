"""API de souscription — reçoit le formulaire du frontend et l'enregistre dans PostgreSQL.

Lancer :
    /opt/anaconda3/bin/python3 -m uvicorn app:app --reload --port 8000
Puis ouvrir : http://localhost:8000
"""
import os
from typing import Optional

import psycopg2
import psycopg2.extras
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# --- Connexion à la base PostgreSQL (le conteneur Docker) ---
DB = dict(host="localhost", port=5432, dbname="souscription",
          user="souscription", password="souscription")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = FastAPI(title="Souscription API")


class Gerant(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    cin: Optional[str] = None


class Inscription(BaseModel):
    """Données envoyées par le formulaire (les champs inconnus sont acceptés)."""
    raison_sociale: Optional[str] = None
    ice: Optional[str] = None
    identifiant_fiscal: Optional[str] = None
    rc_numero: Optional[str] = None
    rc_ville: Optional[str] = None
    organisme: Optional[str] = None          # DOUANE | PORTNET_DOUANE
    type_entite: Optional[str] = None
    type_operateur: Optional[str] = None
    date_commencement: Optional[str] = None
    siege_social: Optional[str] = None
    telephone: Optional[str] = None
    origine: Optional[str] = None
    banque: Optional[str] = None
    gerants: Optional[list[Gerant]] = None   # un OU plusieurs gérants
    model_config = {"extra": "allow"}


def nn(v):
    """Chaîne vide -> None (pour stocker NULL au lieu de '')."""
    return v if (v not in (None, "")) else None


@app.post("/api/inscriptions")
def create_inscription(data: Inscription):
    """Enregistre une inscription (+ son gérant) dans la base."""
    conn = psycopg2.connect(**DB)
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO inscriptions
                 (raison_sociale, ice, rc_numero, rc_ville, identifiant_fiscal, organisme,
                  type_entite, type_operateur, date_commencement, siege_social,
                  telephone, origine, banque, donnees_completes, statut)
               VALUES (%s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s,
                       %s, %s, %s, %s, 'EN_ATTENTE')
               RETURNING id""",
            (nn(data.raison_sociale) or "(sans nom)", nn(data.ice), nn(data.rc_numero),
             nn(data.rc_ville), nn(data.identifiant_fiscal), nn(data.organisme),
             nn(data.type_entite), nn(data.type_operateur), nn(data.date_commencement),
             nn(data.siege_social), nn(data.telephone), nn(data.origine), nn(data.banque),
             psycopg2.extras.Json(data.model_dump())),   # TOUT le formulaire en JSON
        )
        insc_id = cur.fetchone()[0]

        for g in (data.gerants or []):
            if nn(g.nom) or nn(g.cin):
                cur.execute(
                    "INSERT INTO gerants (inscription_id, nom, prenom, cin) VALUES (%s, %s, %s, %s)",
                    (insc_id, nn(g.nom), nn(g.prenom), nn(g.cin)),
                )
        conn.commit()
        return {"ok": True, "id": str(insc_id), "message": "Inscription enregistrée"}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


@app.get("/api/inscriptions")
def list_inscriptions():
    """Liste les inscriptions enregistrées (pour vérifier)."""
    conn = psycopg2.connect(**DB)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""SELECT id, raison_sociale, ice, rc_numero, rc_ville, organisme, statut, cree_le
                       FROM inscriptions ORDER BY cree_le DESC""")
        rows = cur.fetchall()
        return {"count": len(rows), "inscriptions": [dict(r) for r in rows]}
    finally:
        conn.close()


# Sert le frontend (index.html + assets) à la racine -> pas de souci de CORS.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
