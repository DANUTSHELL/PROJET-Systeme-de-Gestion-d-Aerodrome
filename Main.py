from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from CRUD import RequeteSQL

# ==========================================
# 1. INITIALISATION
# ==========================================
app = FastAPI(title="Gestion Aérodrome API", version="2.0.0", description="API complète pour Pilotes et Agents")
db = RequeteSQL("Aerodrome.db")

# ==========================================
# 2. MODÈLES DE DONNÉES (Pydantic)
# ==========================================

class PiloteModel(BaseModel):
    id_pilote: int
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
    id_avion: int
    TypeAvion: str
    Capacite_carburant: int
    id_pilote: int

class MessageModel(BaseModel):
    id_agent: int
    id_pilote: int
    Texte: str

# ==========================================
# 3. ENDPOINTS (ROUTES)
# ==========================================

@app.get("/")
def read_root():
    return {"Status": "Online", "Message": "Bienvenue sur l'API de gestion d'aérodrome."}

# ------------------------------------------
# A. GESTION DES PILOTES
# ------------------------------------------

@app.get("/pilotes", response_model=List[dict])
def get_all_pilotes():
    """(Admin/Agent) Voir tous les pilotes inscrits."""
    raw = db.Select("Pilote")
    return [{"id_pilote": r[0], "Nom": r[1], "Prenom": r[2], "Tel": r[4]} for r in raw]

@app.post("/pilotes")
def create_pilote(pilote: PiloteModel):
    """Inscrire un nouveau pilote et créer son compte."""
    try:
        db.Insert("Compte", [pilote.identifiant, pilote.mot_de_passe])
        valeurs = [pilote.id_pilote, pilote.Nom, pilote.Prenom, pilote.Adresse, pilote.Telephone, pilote.identifiant]
        db.Insert("Pilote", valeurs)
        return {"message": f"Pilote {pilote.Nom} créé avec succès."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur : {str(e)}")

@app.delete("/pilotes/{id_pilote_a_supprimer}")
def delete_pilote(
    id_pilote_a_supprimer: int, 
    requester_role: str = Query(..., description="'Agent' ou 'Pilote'"),
    requester_id: int = Query(..., description="ID de celui qui fait la demande")
):
    """
    Supprimer un pilote.
    Règle : Un Agent peut tout supprimer. Un Pilote ne peut se supprimer que lui-même.
    """

    if requester_role == "Pilote" and requester_id != id_pilote_a_supprimer:
        raise HTTPException(status_code=403, detail="Interdit : Vous ne pouvez pas supprimer un autre pilote.")
    elif requester_role not in ["Agent", "Pilote"]:
        raise HTTPException(status_code=401, detail="Rôle inconnu.")

    try:
        pilote_data = db.Select("Pilote", f"id_pilote = {id_pilote_a_supprimer}")
        if not pilote_data:
            raise HTTPException(status_code=404, detail="Pilote introuvable.")
        
        identifiant_compte = pilote_data[0][5]

        db.Delete("Pilote", "id_pilote", id_pilote_a_supprimer)
        db.Delete("Compte", "identifiant", identifiant_compte)
        
        return {"message": "Pilote et compte supprimés."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/pilotes/{id_pilote}")
def update_pilote(
    id_pilote: int, 
    infos: UpdatePiloteModel,
    requester_role: str = Query(..., description="'Agent' ou 'Pilote'"),
    requester_id: int = Query(..., description="ID du demandeur")
):
    """
    Mettre à jour ses infos (Adresse, Tel).
    Règle : Un pilote modifie uniquement son propre profil.
    """
    if requester_role == "Pilote" and requester_id != id_pilote:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas modifier un autre profil.")
    
    try:
        db.Update("Pilote", "Adresse", infos.Adresse, f"id_pilote = {id_pilote}")
        db.Update("Pilote", "Telephone", infos.Telephone, f"id_pilote = {id_pilote}")
        return {"message": "Profil mis à jour."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------
# B. GESTION DES AVIONS
# ------------------------------------------

@app.post("/avions")
def create_avion(avion: AvionModel):
    """Ajouter un avion."""
    try:
        db.Insert("Avion", [avion.id_avion, avion.TypeAvion, avion.Capacite_carburant, avion.id_pilote])
        return {"message": "Avion ajouté."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mes_avions")
def get_my_avions(id_pilote: int = Query(..., description="Votre ID de pilote")):
    """(Pilote) Voir uniquement mes avions."""
    try:
        raw = db.Select("Avion", f"id_pilote = {id_pilote}")
        return [{"id_avion": r[0], "Modele": r[1], "Capacite": r[2]} for r in raw]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/avions/{id_avion}")
def delete_avion(
    id_avion: int,
    requester_role: str = Query(..., description="'Agent' ou 'Pilote'"),
    requester_id: int = Query(..., description="ID du demandeur")
):
    """
    Supprimer un avion.
    Règle : Un Agent peut tout supprimer. Un Pilote supprime seulement SES avions.
    """
    avion_data = db.Select("Avion", f"id_avion = {id_avion}")
    if not avion_data:
        raise HTTPException(status_code=404, detail="Avion introuvable.")
    
    proprietaire_id = avion_data[0][3]

    if requester_role == "Pilote" and requester_id != proprietaire_id:
        raise HTTPException(status_code=403, detail="Cet avion ne vous appartient pas.")
    
    try:
        db.Delete("Avion", "id_avion", id_avion)
        return {"message": "Avion supprimé."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------
# C. OPÉRATIONS (RÉSERVATIONS & FACTURES)
# ------------------------------------------

@app.get("/mes_reservations")
def get_my_reservations(id_pilote: int = Query(..., description="Votre ID de pilote")):
    """
    (Pilote) Voir ses réservations.
    Logique : On cherche les avions du pilote, puis les réservations liées à ces avions.
    """
    try:
        avions = db.Select("Avion", f"id_pilote = {id_pilote}")
        ids_avions = [a[0] for a in avions]
        
        if not ids_avions:
            return []

        mes_resas = []
        for id_avion in ids_avions:
            resas = db.Select("Reservation", f"id_avion = {id_avion}")
            for r in resas:
                mes_resas.append({
                    "id_reservation": r[0],
                    "Etat": r[1],
                    "Date": r[2],
                    "id_avion": r[5],
                    "id_facture_liee": r[7]
                })
        return mes_resas
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mes_factures")
def get_my_factures(id_pilote: int = Query(..., description="Votre ID de pilote")):
    """
    (Pilote) Voir ses factures.
    Logique complexe : Pilote -> Avion -> Reservation -> Facture
    """
    try:
        avions = db.Select("Avion", f"id_pilote = {id_pilote}")
        ids_avions = [a[0] for a in avions]
        
        if not ids_avions:
            return {"message": "Aucun avion, donc aucune facture."}

        mes_factures = []
        
        for id_avion in ids_avions:
            resas = db.Select("Reservation", f"id_avion = {id_avion}")
            
            for r in resas:
                id_facture = r[7]
                
                facture_data = db.Select("Facture", f"id_facture = {id_facture}")
                if facture_data:
                    f = facture_data[0]
                    mes_factures.append({
                        "id_facture": f[0],
                        "Total_Jour": f[1],   
                        "Total_Global": f[4], 
                        "Concerne_Avion_ID": id_avion,
                        "Date_Reservation": r[2]
                    })
        
        return mes_factures
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------
# D. MESSAGERIE
# ------------------------------------------

@app.post("/messages")
def envoyer_message(msg: MessageModel):
    """Envoyer un message à un agent."""
    try:
        if not db.Select("AgentExploitation", f"id_agent = {msg.id_agent}"):
            raise HTTPException(status_code=404, detail="Agent introuvable")
        
        db.Insert("Message", [msg.id_agent, msg.id_pilote, msg.Texte])
        return {"message": "Message envoyé."}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Une conversation existe déjà avec cet agent (Limitation technique de la BDD actuelle).")

@app.get("/messages")
def lire_mes_messages(
    id_pilote: int = Query(..., description="Votre ID Pilote")
):
    """(Pilote) Lire les messages qui me concernent."""
    try:
        raw = db.Select("Message", f"id_pilote = {id_pilote}")
        messages = []
        for m in raw:
            messages.append({
                "Avec_Agent_ID": m[0],
                "Message": m[2]
            })
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



