from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from CRUD import RequeteSQL

# ==========================================
# 1. INITIALISATION
# ==========================================
app = FastAPI(title="Gestion Aérodrome", version="Final")

db = RequeteSQL("Aerodrome.db")

# ==========================================
# 2. MODÈLES DE DONNÉES (Pydantic)
# ==========================================

class PiloteModel(BaseModel):
    id_pilote: Optional[int] = None 
    Nom: str
    Prenom: str
    Adresse: str
    Telephone: str
    identifiant: str
    mot_de_passe: str 

class UpdatePiloteModel(BaseModel):
    Adresse: str
    Telephone: str

class AvionModel(BaseModel):
    id_avion: Optional[int] = None
    TypeAvion: str
    Capacite_carburant: int
    id_pilote: int

class MessageModel(BaseModel):
    id_agent: int
    id_pilote: int
    Texte: str

class DemandeCreneauModel(BaseModel):
    id_pilote: int
    id_avion: int
    date_souhaitee: str 
    heure_depart: str   
    heure_arrivee: str  
    id_parking_souhaite: int = 1

# ==========================================
# 3. ROUTES (ENDPOINTS)
# ==========================================

@app.get("/")
def read_root():
    return {"Status": "Online", "Message": "API Aérodrome prête."}

# --- IDENTIFICATION ---



# --- GESTION PILOTES ---

@app.get("/pilotes", response_model=List[dict])
def get_all_pilotes():
    """Voir la liste de tous les pilotes."""
    try:
        raw = db.Select("Pilote")
        return [{"id_pilote": r[0], "Nom": r[1], "Prenom": r[2], "Tel": r[4]} for r in raw]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pilotes")
def create_pilote(pilote: PiloteModel):
    """Créer un nouveau pilote (et son compte)."""
    try:
        db.Insert("Compte", [pilote.identifiant, pilote.mot_de_passe])
        
        valeurs = [None, pilote.Nom, pilote.Prenom, pilote.Adresse, pilote.Telephone, pilote.identifiant]
        db.Insert("Pilote", valeurs)
        
        new_id = db.cur.lastrowid
        return {"message": "Pilote créé avec succès", "id_genere": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur (Doublon ou données invalides) : {str(e)}")

@app.delete("/pilotes/{id_pilote}")
def delete_pilote(id_pilote: int, requester_role: str = Query(...), requester_id: int = Query(...)):
    """Supprimer un pilote (Agent = Tout, Pilote = Soi-même)."""
    
    if requester_role == "Pilote":
        if requester_id != id_pilote:
            raise HTTPException(status_code=403, detail="Vous ne pouvez pas supprimer un autre pilote.")
    elif requester_role != "Agent":
        raise HTTPException(status_code=401, detail="Rôle inconnu (Doit être 'Agent' ou 'Pilote').")

    try:
        data = db.Select("Pilote", f"id_pilote = {id_pilote}")
        if not data:
            raise HTTPException(status_code=404, detail="Pilote introuvable.")
        
        identifiant_compte = data[0][5]

        db.Delete("Pilote", "id_pilote", id_pilote)
        db.Delete("Compte", "identifiant", identifiant_compte)
        
        return {"message": f"Pilote {id_pilote} supprimé."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- GESTION AVIONS ---

@app.post("/avions")
def create_avion(avion: AvionModel):
    try:
        db.Insert("Avion", [None, avion.TypeAvion, avion.Capacite_carburant, avion.id_pilote])
        return {"message": "Avion ajouté", "id_avion": db.cur.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mes_avions")
def get_my_avions(id_pilote: int = Query(...)):
    raw = db.Select("Avion", f"id_pilote = {id_pilote}")
    return [{"id_avion": r[0], "Modele": r[1], "Capacite": r[2]} for r in raw]

# --- GESTION DES CRÉNEAUX (RÉSERVATIONS) ---

@app.post("/demande_creneau")
def demander_creneau(demande: DemandeCreneauModel):
    """
    Le pilote demande un créneau.
    Cela crée automatiquement : Vol + Facture (vide) + Réservation.
    """
    try:
        db.Insert("Vol", [None, demande.heure_depart, demande.heure_arrivee])
        id_vol = db.cur.lastrowid

        db.Insert("Facture", [None, 0, 0, 0, 0, 1]) 
        id_facture = db.cur.lastrowid

        db.Insert("Reservation", [
            None, 
            "En attente", 
            demande.date_souhaitee, 
            "Non", 
            id_vol, 
            demande.id_avion, 
            demande.id_parking_souhaite, 
            id_facture
        ])
        
        return {"message": "Demande envoyée", "id_reservation": db.cur.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur technique : {str(e)}")

@app.get("/agent/reservations")
def voir_reservations(requester_role: str = Query(...)):
    """L'agent voit toutes les réservations."""
    
    if requester_role != "Agent":
        raise HTTPException(status_code=403, detail="Accès réservé aux Agents.")

    raw = db.Select("Reservation")
    resultat = []
    for r in raw:
        resultat.append({
            "id_reservation": r[0],
            "Etat": r[1],
            "Date": r[2],
            "Disponibilite": r[3],
            "id_avion": r[5]
        })
    return resultat

@app.put("/agent/reservations/{id_resa}/decision")
def decision_agent(id_resa: int, decision: str, requester_role: str = Query(...)):
    """Valider ou Refuser une réservation."""
    
    if requester_role != "Agent":
        raise HTTPException(status_code=403, detail="Accès réservé aux Agents.")
    
    if decision not in ["Confirmée", "Refusée"]:
        raise HTTPException(status_code=400, detail="Décision invalide (choisir 'Confirmée' ou 'Refusée').")

    try:
        db.Update("Reservation", "Etat", decision, f"id_reservation = {id_resa}")
        
        dispo = "Oui" if decision == "Confirmée" else "Non"
        db.Update("Reservation", "Dispo", dispo, f"id_reservation = {id_resa}")
        
        return {"message": f"Réservation {id_resa} passée à {decision}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- MESSAGERIE ---

@app.post("/messages")
def envoyer_message(msg: MessageModel):
    try:
        try:
            db.Insert("Message", [msg.id_agent, msg.id_pilote, msg.Texte])
        except:
            db.Update("Message", "Texte", f"'{msg.Texte}'", f"id_agent={msg.id_agent} AND id_pilote={msg.id_pilote}")
        
        return {"message": "Envoyé"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/messages")
def lire_messages(id_pilote: int = Query(...)):
    raw = db.Select("Message", f"id_pilote = {id_pilote}")
    return [{"Agent_ID": r[0], "Message": r[2]} for r in raw]
