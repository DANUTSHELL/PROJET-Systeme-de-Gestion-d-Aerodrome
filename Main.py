from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from CRUD import RequeteSQL

# 1. Initialisation de l'application et de la BDD
app = FastAPI(title="Gestion Aérodrome API", version="1.0.0")
db = RequeteSQL("Aerodrome.db")

# 2. Modèles de données (Pydantic)
# Ces classes servent à valider les données envoyées par l'utilisateur
# C'est comme un "moule" pour vérifier que les données sont correctes.

class PiloteModel(BaseModel):
    id_pilote: int
    Nom: str
    Prenom: str
    Adresse: str
    Telephone: str
    identifiant: str

class AvionModel(BaseModel):
    id_avion: int
    TypeAvion: str
    Capacite_carburant: int
    id_pilote: int

# 3. Les Routes (Endpoints)

@app.get("/")
def read_root():
    return {"Message": "Bienvenue sur l'API de l'Aérodrome. Allez sur /docs pour tester."}

# --- GESTION DES PILOTES ---

@app.get("/pilotes", response_model=List[dict])
def get_all_pilotes():
    """Récupère la liste de tous les pilotes"""
    raw_data = db.Select("Pilote")
    
    # Transformation : La BDD renvoie des tuples (1, 'Dupont'...), 
    # l'API doit renvoyer du JSON (dictionnaire).
    pilotes_json = []
    for row in raw_data:
        pilotes_json.append({
            "id_pilote": row[0],
            "Nom": row[1],
            "Prenom": row[2],
            "Adresse": row[3],
            "Telephone": row[4],
            "identifiant": row[5]
        })
    return pilotes_json

@app.get("/pilotes/{id_pilote}")
def get_pilote_by_id(id_pilote: int):
    """Récupère un pilote spécifique par son ID"""
    condition = f"id_pilote = {id_pilote}" # Attention aux injections SQL ici normalement
    data = db.Select("Pilote", conditions=condition)
    
    if not data:
        raise HTTPException(status_code=404, detail="Pilote non trouvé")
    
    row = data[0]
    return {
        "id_pilote": row[0],
        "Nom": row[1],
        "Prenom": row[2],
        "Adresse": row[3],
        "Telephone": row[4],
        "identifiant": row[5]
    }

@app.post("/pilotes")
def create_pilote(pilote: PiloteModel):
    """Ajoute un nouveau pilote"""
    try:
        # On transforme l'objet Pydantic en liste pour ta fonction Insert
        valeurs = [pilote.id_pilote, pilote.Nom, pilote.Prenom, pilote.Adresse, pilote.Telephone, pilote.identifiant]
        db.Insert("Pilote", valeurs)
        return {"message": "Pilote ajouté avec succès", "data": pilote}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'insertion : {str(e)}")

@app.delete("/pilotes/{id_pilote}")
def delete_pilote(id_pilote: int):
    """Supprime un pilote"""
    try:
        # Note : Ta fonction Delete attend (nomTable, condition_colonne, valeur)
        # Assure-toi que ton CRUD.py a bien la signature : Delete(nomTable, col, val)
        # Si tu utilises l'ancienne version : Delete(nomTable, "id_pilote = ...")
        
        # Version sécurisée (si tu as utilisé mon code CRUD corrigé précédent) :
        db.Delete("Pilote", "id_pilote", id_pilote)
        
        # Si tu as gardé TA version originale de CRUD, utilise plutôt :
        # db.Delete("Pilote", f"id_pilote = {id_pilote}")
        
        return {"message": f"Pilote {id_pilote} supprimé."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur : {str(e)}")

# --- GESTION DES AVIONS (Exemple rapide) ---

@app.get("/avions")
def get_avions():
    raw_data = db.Select("Avion")
    avions = []
    for row in raw_data:
        avions.append({
            "id_avion": row[0],
            "Type": row[1],
            "Capacite": row[2],
            "Proprietaire_ID": row[3]
        })
    return avions

@app.post("/avions")
def create_avion(avion: AvionModel):
    try:
        valeurs = [avion.id_avion, avion.TypeAvion, avion.Capacite_carburant, avion.id_pilote]
        db.Insert("Avion", valeurs)
        return {"message": "Avion ajouté", "avion": avion}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))