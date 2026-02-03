from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from CRUD import RequeteSQL

# 1. Initialisation
app = FastAPI(title="Gestion Aérodrome API", version="1.1.0")
db = RequeteSQL("Aerodrome.db")

# 2. Modèles de données (Pydantic)
class PiloteModel(BaseModel):
    id_pilote: int
    Nom: str
    Prenom: str
    Adresse: str
    Telephone: str
    identifiant: str
    mot_de_passe: str

class AvionModel(BaseModel):
    id_avion: int
    TypeAvion: str
    Capacite_carburant: int
    id_pilote: int

# 3. Endpoints

@app.get("/")
def read_root():
    return {"Message": "API Aérodrome opérationnelle. Règles métier actives."}

# --- GESTION DES PILOTES ---

@app.get("/pilotes", response_model=List[dict])
def get_all_pilotes():
    """Récupère tous les pilotes."""
    raw = db.Select("Pilote")
    return [{"id_pilote": r[0], "Nom": r[1], "Prenom": r[2], "identifiant": r[5]} for r in raw]

@app.post("/pilotes")
def create_pilote(pilote: PiloteModel):
    """Crée un pilote ET son compte associé."""
    try:
        db.Insert("Compte", [pilote.identifiant, pilote.mot_de_passe])
        valeurs = [pilote.id_pilote, pilote.Nom, pilote.Prenom, pilote.Adresse, pilote.Telephone, pilote.identifiant]
        db.Insert("Pilote", valeurs)
        return {"message": "Pilote et Compte créés avec succès."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur : {str(e)}")

@app.delete("/pilotes/{id_pilote_a_supprimer}")
def delete_pilote(
    id_pilote_a_supprimer: int, 
    requester_role: str = Query(..., description="Role du demandeur: 'Agent' ou 'Pilote'"),
    requester_id: int = Query(..., description="ID de celui qui fait la demande")
):
    """
    Supprime un pilote et son compte.
    RÈGLE : Un Agent peut tout supprimer. Un Pilote ne peut se supprimer que lui-même.
    """
    # 1. Vérification des droits
    if requester_role == "Pilote":
        if requester_id != id_pilote_a_supprimer:
            raise HTTPException(status_code=403, detail="Interdit : Vous ne pouvez pas supprimer un autre pilote que vous-même.")
    elif requester_role != "Agent":
        raise HTTPException(status_code=401, detail="Rôle inconnu.")

    try:
        # 2. Récupérer l'identifiant du compte AVANT de supprimer le pilote
        pilote_data = db.Select("Pilote", f"id_pilote = {id_pilote_a_supprimer}")
        if not pilote_data:
            raise HTTPException(status_code=404, detail="Pilote introuvable.")
        
        identifiant_compte = pilote_data[0][5]

        db.Delete("Pilote", "id_pilote", id_pilote_a_supprimer)
        db.Delete("Compte", "identifiant", identifiant_compte)
        
        return {"message": f"Pilote {id_pilote_a_supprimer} et son compte associé ont été supprimés."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur technique : {str(e)}")

# --- GESTION DES AVIONS ---

@app.post("/avions")
def create_avion(avion: AvionModel):
    try:
        db.Insert("Avion", [avion.id_avion, avion.TypeAvion, avion.Capacite_carburant, avion.id_pilote])
        return {"message": "Avion ajouté."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/avions/{id_avion_a_supprimer}")
def delete_avion(
    id_avion_a_supprimer: int,
    requester_role: str = Query(..., description="Role du demandeur: 'Agent' ou 'Pilote'"),
    requester_id: int = Query(..., description="ID de celui qui fait la demande")
):
    """
    Supprime un avion.
    RÈGLE : Un Agent peut tout supprimer. Un Pilote ne peut supprimer que SES avions.
    """
    avion_data = db.Select("Avion", f"id_avion = {id_avion_a_supprimer}")
    if not avion_data:
        raise HTTPException(status_code=404, detail="Avion introuvable.")
    
    proprietaire_id = avion_data[0][3]

    # 2. Vérification des droits
    if requester_role == "Pilote":
        if requester_id != proprietaire_id:
            raise HTTPException(status_code=403, detail="Interdit : Cet avion ne vous appartient pas.")
    elif requester_role != "Agent":
        raise HTTPException(status_code=401, detail="Rôle inconnu.")

    # 3. Suppression
    try:
        db.Delete("Avion", "id_avion", id_avion_a_supprimer)
        return {"message": f"Avion {id_avion_a_supprimer} supprimé avec succès."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
