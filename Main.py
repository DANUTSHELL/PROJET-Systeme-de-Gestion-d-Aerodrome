from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from CRUD import RequeteSQL

# ==========================================
# 1. INITIALISATION & UTILITAIRES
# ==========================================
app = FastAPI(title="Gestion Aérodrome API", version="3.0.0", description="Système complet Pilotes & Agents")
db = RequeteSQL("Aerodrome.db")

# Fonction pour générer automatiquement les IDs (car pas d'AUTOINCREMENT configuré)
def get_next_id(table_name: str, id_column: str) -> int:
    try:
        # On récupère tous les IDs, on les trie et on prend le dernier + 1
        # Note: Ce n'est pas le plus performant pour le Big Data, mais parfait pour ce projet.
        rows = db.Select(table_name)
        if not rows:
            return 1
        ids = [row[0] for row in rows] # On suppose que l'ID est toujours en première position (index 0)
        return max(ids) + 1
    except:
        return 1

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

# Modèle pour demander un créneau (Réservation)
class DemandeCreneauModel(BaseModel):
    id_pilote: int
    id_avion: int
    date_souhaitee: str # Format JJ/MM/AAAA
    heure_depart: str   # Format HH:MM
    heure_arrivee: str  # Format HH:MM
    id_parking_souhaite: int = 1 # Par défaut parking 1

# ==========================================
# 3. ENDPOINTS (ROUTES)
# ==========================================

@app.get("/")
def read_root():
    return {"Status": "Online", "Message": "API Aérodrome V3 - Gestion des Créneaux active"}

# ------------------------------------------
# A. GESTION DES PILOTES & COMPTES
# ------------------------------------------
# (Identique à avant, juste condensé pour la lisibilité)

@app.get("/pilotes", response_model=List[dict])
def get_all_pilotes():
    raw = db.Select("Pilote")
    return [{"id_pilote": r[0], "Nom": r[1], "Prenom": r[2], "Tel": r[4]} for r in raw]

@app.post("/pilotes")
def create_pilote(pilote: PiloteModel):
    try:
        db.Insert("Compte", [pilote.identifiant, pilote.mot_de_passe])
        valeurs = [pilote.id_pilote, pilote.Nom, pilote.Prenom, pilote.Adresse, pilote.Telephone, pilote.identifiant]
        db.Insert("Pilote", valeurs)
        return {"message": "Pilote créé."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/pilotes/{id_pilote}")
def update_pilote(id_pilote: int, infos: UpdatePiloteModel, requester_role: str = Query(...), requester_id: int = Query(...)):
    if requester_role == "Pilote" and requester_id != id_pilote:
        raise HTTPException(status_code=403, detail="Interdit.")
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
    try:
        db.Insert("Avion", [avion.id_avion, avion.TypeAvion, avion.Capacite_carburant, avion.id_pilote])
        return {"message": "Avion ajouté."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/mes_avions")
def get_my_avions(id_pilote: int = Query(...)):
    raw = db.Select("Avion", f"id_pilote = {id_pilote}")
    return [{"id_avion": r[0], "Modele": r[1]} for r in raw]

# ------------------------------------------
# C. GESTION DES CRÉNEAUX (RÉSERVATIONS) -- NOUVEAU --
# ------------------------------------------

@app.post("/demande_creneau")
def demander_creneau(demande: DemandeCreneauModel):
    """
    (Pilote) Demander une réservation.
    Crée un Vol, une Facture (vide) et la Réservation en statut 'En attente'.
    """
    try:
        # 1. Génération des IDs automatiques
        next_id_vol = get_next_id("Vol", "id_vol")
        next_id_facture = get_next_id("Facture", "id_facture")
        next_id_resa = get_next_id("Reservation", "id_reservation")

        # 2. Création du Vol
        # Table Vol: id_vol, Heure_depart, Heure_arrivee
        db.Insert("Vol", [next_id_vol, demande.heure_depart, demande.heure_arrivee])

        # 3. Création d'une Facture provisoire (montant 0, pas d'agent assigné pour l'instant - on met 1 par défaut)
        # Table Facture: id, r_jour, r_mois, r_annee, total, id_agent
        # On initialise à 0€
        db.Insert("Facture", [next_id_facture, 0, 0, 0, 0, 1]) 

        # 4. Création de la Réservation "En attente"
        # Table Reservation: id, Etat, Date, Dispo, id_vol, id_avion, id_parking, id_facture
        db.Insert("Reservation", [
            next_id_resa, 
            "En attente", 
            demande.date_souhaitee, 
            "Non", # Dispo (Non validé encore)
            next_id_vol, 
            demande.id_avion, 
            demande.id_parking_souhaite, 
            next_id_facture
        ])

        return {"message": "Votre demande est enregistrée. En attente de validation par l'agent.", "id_reservation": next_id_resa}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur technique : {str(e)}")

@app.get("/agent/reservations")
def voir_toutes_reservations(requester_role: str = Query(..., regex="^Agent$")):
    """(Agent) Voir toutes les demandes de créneaux."""
    try:
        raw = db.Select("Reservation")
        # On formate pour que l'agent comprenne vite
        return [{
            "id_reservation": r[0],
            "Etat": r[1],
            "Date": r[2],
            "Disponibilite_Confirmee": r[3],
            "Avion_ID": r[5],
            "Facture_ID": r[7]
        } for r in raw]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/agent/reservations/{id_reservation}/decision")
def valider_ou_refuser_creneau(
    id_reservation: int, 
    decision: str = Query(..., description="'Confirmée' ou 'Refusée'"),
    requester_role: str = Query(..., regex="^Agent$")
):
    """
    (Agent) Valider ou Refuser un créneau.
    Si confirmé, on passe Dispo à 'Oui'.
    """
    if decision not in ["Confirmée", "Refusée"]:
        raise HTTPException(status_code=400, detail="La décision doit être 'Confirmée' ou 'Refusée'.")
    
    try:
        # Mise à jour de l'état
        db.Update("Reservation", "Etat", decision, f"id_reservation = {id_reservation}")
        
        # Si confirmé, on dit que le créneau est Dispo
        nouvelle_dispo = "Oui" if decision == "Confirmée" else "Non"
        db.Update("Reservation", "Dispo", nouvelle_dispo, f"id_reservation = {id_reservation}")
        
        return {"message": f"La réservation {id_reservation} est maintenant {decision}."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------
# D. GESTION FACTURATION (AGENT) -- NOUVEAU --
# ------------------------------------------

@app.put("/agent/factures/{id_facture}/calculer")
def generer_facture(
    id_facture: int,
    montant_total: float,
    id_agent_responsable: int,
    requester_role: str = Query(..., regex="^Agent$")
):
    """
    (Agent) Finaliser une facture après un vol.
    Met à jour le montant et l'agent responsable.
    """
    try:
        # On met à jour le total et l'agent
        db.Update("Facture", "total", montant_total, f"id_facture = {id_facture}")
        db.Update("Facture", "id_agent", id_agent_responsable, f"id_facture = {id_facture}")
        
        # Pour faire simple, on remplit r_jour/mois/annee avec le même montant (simplification)
        # Idéalement, il faudrait des calculs séparés
        db.Update("Facture", "r_jour", montant_total, f"id_facture = {id_facture}")
        
        return {"message": f"Facture {id_facture} mise à jour : {montant_total} €"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------------------------------
# E. MESSAGERIE
# ------------------------------------------

@app.post("/messages")
def envoyer_message(msg: MessageModel):
    """Envoyer un message."""
    try:
        # On tente d'insérer. Si ça plante (clé primaire existe), on met à jour.
        # C'est une astuce car ta table Message a une clé primaire (id_agent, id_pilote)
        # ce qui empêche d'avoir plusieurs messages entre les deux mêmes personnes.
        try:
            db.Insert("Message", [msg.id_agent, msg.id_pilote, msg.Texte])
            return {"message": "Nouveau message envoyé."}
        except:
            # Si ça existe déjà, on remplace le texte (Update)
            db.Update("Message", "Texte", f"'{msg.Texte}'", f"id_agent={msg.id_agent} AND id_pilote={msg.id_pilote}")
            return {"message": "Message précédent mis à jour (limite de la BDD actuelle)."}
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
