from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
from CRUD import RequeteSQL
from datetime import datetime

# ==========================================
# 1. INITIALISATION
# ==========================================
app = FastAPI(
    title="Système de Gestion d'Aérodrome",
    description="API pour Agent d'Exploitation, Gestionnaire et Pilote",
    version="Final"
)

db = RequeteSQL("Aerodrome.db")

# ==========================================
# 2. MODÈLES DE DONNÉES (Pydantic)
# ==========================================

# --- Modèles de base ---
class PiloteModel(BaseModel):
    id_pilote: Optional[int] = None 
    Nom: str
    Prenom: str
    Adresse: str
    Telephone: str
    identifiant: str
    mot_de_passe: str 

class AvionModel(BaseModel):
    id_avion: Optional[int] = None
    TypeAvion: str
    Capacite_carburant: int
    id_pilote: int

class DemandeCreneauModel(BaseModel):
    id_pilote: int
    id_avion: int
    date_souhaitee: str 
    heure_depart: str   
    heure_arrivee: str  
    id_parking_souhaite: int = 1

# --- Modèles pour l'Agent ---
class AjoutServiceCarburant(BaseModel):
    id_reservation: int
    quantite: float
    type_carburant: Literal["AVGAS 100LL", "JET A1"]

class AjoutServiceHangar(BaseModel):
    id_reservation: int
    id_hangar: int

class ValidationCreneau(BaseModel):
    decision: str  # "Confirmée", "Autorisée", "Achevée", "Annulée"

# --- Modèles pour le Gestionnaire ---
class UpdatePrixCarburant(BaseModel):
    type_carburant: str
    nouveau_prix: float

class NouveauHangar(BaseModel):
    Taille: str
    Prix_jour: float
    Prix_semaine: float
    Prix_mois: float

# --- Modèles pour la Messagerie ---
class MessageEnvoi(BaseModel):
    id_agent: int
    id_pilote: int
    texte: str

# ==========================================
# 3. FONCTIONS UTILITAIRES
# ==========================================

def verifier_role(role_attendu: str, role_recu: str):
    """Vérifie si l'utilisateur a le droit d'accéder."""
    if role_recu != role_attendu:
        raise HTTPException(status_code=403, detail=f"Accès refusé. Réservé au rôle : {role_attendu}")

# ==========================================
# 4. PARTIE COMMUNE (LOGIN / PILOTES)
# ==========================================

@app.get("/")
def read_root():
    return {"System": "Online", "Roles": ["Pilote", "Agent", "Gestionnaire"]}

@app.post("/pilotes/inscription", tags=["Authentification"])
def inscription_pilote(pilote: PiloteModel):
    """Permet à un pilote de s'inscrire."""
    try:
        db.Insert("Compte", [pilote.identifiant, pilote.mot_de_passe, "Pilote"])
        valeurs = [None, pilote.Nom, pilote.Prenom, pilote.Adresse, pilote.Telephone, pilote.identifiant]
        db.Insert("Pilote", valeurs)
        return {"message": "Inscription réussie", "id_genere": db.cur.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ==========================================
# 5. ESPACE AGENT D'EXPLOITATION
# ==========================================

TAG_AGENT = "Agent d'Exploitation"

# --- A. GESTION DES PILOTES ---

@app.get("/agent/pilotes", tags=[TAG_AGENT])
def lister_pilotes(role: str = Query(..., description="Doit être 'Agent'")):
    verifier_role("Agent", role)
    raw = db.Select("Pilote")
    return [{"id": r[0], "Nom": r[1], "Prenom": r[2], "Tel": r[4]} for r in raw]

@app.delete("/agent/pilotes/{id_pilote}", tags=[TAG_AGENT])
def supprimer_pilote(id_pilote: int, role: str = Query(..., description="Doit être 'Agent'")):
    verifier_role("Agent", role)
    try:
        p = db.Select("Pilote", f"id_pilote={id_pilote}")
        if not p: raise HTTPException(404, "Pilote introuvable")
        identifiant = p[0][5]
        
        db.Delete("Pilote", "id_pilote", id_pilote)
        db.Delete("Compte", "identifiant", identifiant)
        return {"message": "Pilote supprimé"}
    except Exception as e:
        raise HTTPException(400, str(e))

# --- B. GESTION DES CRÉNEAUX (DISPONIBILITÉ) ---

@app.get("/agent/creneaux", tags=[TAG_AGENT])
def voir_tous_creneaux(role: str = Query(..., description="Doit être 'Agent'")):
    verifier_role("Agent", role)
    raw = db.Select("Reservation")
    return [{"id": r[0], "Etat": r[1], "Date": r[2], "Dispo": r[3], "Avion": r[5]} for r in raw]

@app.put("/agent/creneaux/{id_resa}/statut", tags=[TAG_AGENT])
def modifier_statut_creneau(id_resa: int, validation: ValidationCreneau, role: str = Query(..., description="Doit être 'Agent'")):
    """
    1. Ajouter, modifier ou annuler un créneau.
    États possibles : 'Confirmée', 'Autorisée', 'Achevée', 'Annulée'.
    """
    verifier_role("Agent", role)
    try:
        db.Update("Reservation", "Etat", validation.decision, f"id_reservation={id_resa}")
        
        if validation.decision in ["Annulée", "Achevée"]:
            dispo = "Non"
        else:
            dispo = "Oui"
            
        db.Update("Reservation", "Dispo", dispo, f"id_reservation={id_resa}")
        
        return {"message": f"Créneau {id_resa} passé à {validation.decision} (Dispo: {dispo})"}
    except Exception as e:
        raise HTTPException(400, str(e))

# --- C. GESTION DES SERVICES AU SOL (AFFECTATION RESSOURCES) ---

@app.post("/agent/services/carburant", tags=[TAG_AGENT])
def ajouter_service_carburant(service: AjoutServiceCarburant, role: str = Query(..., description="Doit être 'Agent'")):
    """2. Affecter les ressources (Carburant) à une réservation."""
    verifier_role("Agent", role)
    try:
        db.Insert("Remplir", [service.id_reservation, service.quantite, service.type_carburant])
        return {"message": f"{service.quantite}L de {service.type_carburant} ajoutés."}
    except Exception as e:
        raise HTTPException(400, "Erreur (Déjà ravitaillé ?): " + str(e))

@app.post("/agent/services/hangar", tags=[TAG_AGENT])
def affecter_hangar(service: AjoutServiceHangar, role: str = Query(..., description="Doit être 'Agent'")):
    """2. Affecter les ressources (Hangar) à une réservation."""
    verifier_role("Agent", role)
    try:
        db.Insert("Emplacement", [None, service.id_reservation, service.id_hangar])
        return {"message": f"Hangar {service.id_hangar} réservé pour la réservation {service.id_reservation}"}
    except Exception as e:
        raise HTTPException(400, str(e))

# --- D. GESTION DES FACTURES ---

@app.post("/agent/factures/{id_reservation}/generer", tags=[TAG_AGENT])
def generer_facture(id_reservation: int, id_agent: int, role: str = Query(..., description="Doit être 'Agent'")):
    """
    3. Calculer et générer la facture.
    Logique : Prix Parking + (Prix Carburant * Qté) + Prix Hangar
    """
    verifier_role("Agent", role)
    try:
        total = 0.0
        
        resa = db.Select("Reservation", f"id_reservation={id_reservation}")
        if not resa: raise HTTPException(404, "Réservation introuvable")
        id_parking = resa[0][6]
        id_facture = resa[0][7]
        
        # 1. Coût Parking
        park = db.Select("Parking", f"id_parking={id_parking}")
        if park:
            code_prix = park[0][2]
            total += 50.0 if code_prix == 'A' else 20.0
            
        # 2. Coût Carburant
        remplir = db.Select("Remplir", f"id_reservation={id_reservation}")
        if remplir:
            qte = remplir[0][1]
            type_c = remplir[0][2]
            carb_info = db.Select("Carburant", f"Type_carburant='{type_c}'")
            if carb_info:
                prix_L = carb_info[0][1]
                total += (qte * prix_L)

        empl = db.Select("Emplacement", f"id_reservation={id_reservation}")
        if empl:
            id_hangar = empl[0][2]
            hangar = db.Select("Hangar", f"id_hangar={id_hangar}")
            if hangar:
                total += hangar[0][2]

        db.Update("Facture", "total", total, f"id_facture={id_facture}")
        db.Update("Facture", "id_agent", id_agent, f"id_facture={id_facture}")
        
        db.Update("Facture", "r_jour", total, f"id_facture={id_facture}")
        db.Update("Facture", "r_mois", total, f"id_facture={id_facture}")
        db.Update("Facture", "r_annee", total, f"id_facture={id_facture}")

        return {"message": "Facture générée", "Total_Calculé": total, "id_facture": id_facture}

    except Exception as e:
        raise HTTPException(400, str(e))

# --- E. MESSAGERIE (Réponse Agent) ---
@app.post("/agent/message/reponse", tags=[TAG_AGENT])
def repondre_message(msg: MessageEnvoi, role: str = Query(..., description="Doit être 'Agent'")):
    """L'agent répond au pilote."""
    verifier_role("Agent", role)
    try:
        db.Update("Message", "Texte", f"'{msg.texte}'", f"id_agent={msg.id_agent} AND id_pilote={msg.id_pilote}")
        return {"message": "Réponse envoyée."}
    except Exception as e:
        raise HTTPException(400, str(e))


# ==========================================
# 6. ESPACE GESTIONNAIRE D'AÉRODROME
# ==========================================

TAG_GEST = "Gestionnaire d'Aérodrome"

# --- A. VISUALISER LE FLUX DES MOUVEMENTS ---

@app.get("/gestionnaire/flux", tags=[TAG_GEST])
def visualiser_flux(role: str = Query(..., description="Doit être 'Gestionnaire'")):
    """1. Visualiser le flux des mouvements par état."""
    verifier_role("Gestionnaire", role)
    try:
        all_resas = db.Select("Reservation")
        stats = {"Demandé": 0, "Confirmée": 0, "Autorisée": 0, "Achevée": 0, "Annulée": 0}
        
        for r in all_resas:
            etat = r[1]
            if etat in stats: stats[etat] += 1
            
        return stats
    except Exception as e:
        raise HTTPException(500, str(e))

# --- B. GÉRER LES INFRASTRUCTURES ---

@app.get("/gestionnaire/infrastructures", tags=[TAG_GEST])
def etat_infrastructures(role: str = Query(..., description="Doit être 'Gestionnaire'")):
    """Voir l'état des stocks et places."""
    verifier_role("Gestionnaire", role)
    carburants = db.Select("Carburant")
    hangars = db.Select("Hangar")
    parkings = db.Select("Parking")
    
    return {
        "Carburants": [{"Type": c[0], "Prix": c[1], "Stock_Max": c[2]} for c in carburants],
        "Hangars_Total": len(hangars),
        "Parkings_Total": len(parkings)
    }

@app.put("/gestionnaire/infrastructure/carburant", tags=[TAG_GEST])
def changer_prix_carburant(modif: UpdatePrixCarburant, role: str = Query(..., description="Doit être 'Gestionnaire'")):
    """2. Gérer l'infrastructure : Modifier prix carburant."""
    verifier_role("Gestionnaire", role)
    try:
        db.Update("Carburant", "prix_litre", modif.nouveau_prix, f"Type_carburant='{modif.type_carburant}'")
        return {"message": "Prix mis à jour."}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/gestionnaire/infrastructure/hangar", tags=[TAG_GEST])
def ajouter_hangar(h: NouveauHangar, role: str = Query(..., description="Doit être 'Gestionnaire'")):
    """2. Gérer l'infrastructure : Ajouter un nouveau hangar."""
    verifier_role("Gestionnaire", role)
    try:
        db.Insert("Hangar", [None, h.Taille, h.Prix_jour, h.Prix_semaine, h.Prix_mois])
        return {"message": "Nouveau hangar construit."}
    except Exception as e:
        raise HTTPException(400, str(e))

# --- C. SUIVI DES RECETTES & D. RAPPORT ---

@app.get("/gestionnaire/rapport_financier", tags=[TAG_GEST])
def generer_rapport(role: str = Query(..., description="Doit être 'Gestionnaire'")):
    """3. Suivi des recettes et rapport complet."""
    verifier_role("Gestionnaire", role)
    try:
        factures = db.Select("Facture")
        recette_totale = sum([f[4] for f in factures])
        
        rapport = {
            "Date_Generation": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Volume_Ventes": len(factures),
            "Recettes_Globales": recette_totale,
            "Analyse": {
                "Recette_Mensuelle_Estimee": recette_totale / 12,
                "Recette_Annuelle_Reelle": recette_totale
            }
        }
        return rapport
    except Exception as e:
        raise HTTPException(500, str(e))


# ==========================================
# 7. ESPACE PILOTE
# ==========================================

TAG_PILOTE = "Espace Pilote"

@app.get("/pilote/mes_avions", tags=[TAG_PILOTE])
def voir_mes_avions(id_pilote: int, role: str = Query(..., description="Doit être 'Pilote'")):
    """Le pilote consulte ses avions."""
    verifier_role("Pilote", role)
    raw = db.Select("Avion", f"id_pilote={id_pilote}")
    return [{"id": r[0], "Type": r[1], "Capa": r[2]} for r in raw]

@app.post("/pilote/mes_avions", tags=[TAG_PILOTE])
def ajouter_avion(avion: AvionModel, role: str = Query(..., description="Doit être 'Pilote'")):
    """Le pilote ajoute un aéronef."""
    verifier_role("Pilote", role)
    try:
        db.Insert("Avion", [None, avion.TypeAvion, avion.Capacite_carburant, avion.id_pilote])
        return {"message": "Avion ajouté", "id_avion": db.cur.lastrowid}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/pilote/demande_creneau", tags=[TAG_PILOTE])
def demander_creneau_pilote(demande: DemandeCreneauModel):
    """Demande de réservation avec vérification automatique de disponibilité."""
    try:
        # --- 1. VÉRIFICATION AUTOMATIQUE DE DISPONIBILITÉ ---
        condition = f"Date = '{demande.date_souhaitee}' AND id_parking = {demande.id_parking_souhaite} AND Etat != 'Annulée' AND Etat != 'Achevée'"
        conflits = db.Select("Reservation", condition)

        if len(conflits) > 0:
            etat_auto = "Annulée"
            dispo_auto = "Non"
            message_retour = "Demande rejetée automatiquement : Parking indisponible à cette date."
        else:
            etat_auto = "Demandé"
            dispo_auto = "Oui"    
            message_retour = "Disponibilité OK : Demande envoyée à l'agent."

        # --- 2. CRÉATION DES ENREGISTREMENTS ---
        db.Insert("Vol", [None, demande.heure_depart, demande.heure_arrivee])
        id_vol = db.cur.lastrowid
        
        db.Insert("Facture", [None, 0, 0, 0, 0, 1]) 
        id_fac = db.cur.lastrowid
        
        db.Insert("Reservation", [None, etat_auto, demande.date_souhaitee, dispo_auto, id_vol, demande.id_avion, demande.id_parking_souhaite, id_fac])
        
        return {
            "message": message_retour, 
            "Etat_Attribué": etat_auto, 
            "id_reservation": db.cur.lastrowid
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/pilote/mes_factures", tags=[TAG_PILOTE])
def consulter_mes_factures(id_pilote: int, role: str = Query(..., description="Doit être 'Pilote'")):
    """Voir historique factures."""
    verifier_role("Pilote", role)
    try:
        avions = db.Select("Avion", f"id_pilote={id_pilote}")
        ids_avions = [a[0] for a in avions]
        mes_factures = []

        for id_avion in ids_avions:
            resas = db.Select("Reservation", f"id_avion={id_avion}")
            for r in resas:
                f_data = db.Select("Facture", f"id_facture={r[7]}")
                if f_data:
                    mes_factures.append({
                        "Date": r[2],
                        "Montant": f_data[0][4],
                        "Statut": r[1]
                    })
        return mes_factures
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pilote/message", tags=[TAG_PILOTE])
def ecrire_message_pilote(msg: MessageEnvoi, role: str = Query(..., description="Doit être 'Pilote'")):
    """Le pilote envoie un message."""
    verifier_role("Pilote", role)
    try:
        try:
            db.Insert("Message", [msg.id_agent, msg.id_pilote, msg.texte])
        except:
            db.Update("Message", "Texte", f"'{msg.texte}'", f"id_agent={msg.id_agent} AND id_pilote={msg.id_pilote}")
        return {"message": "Message envoyé."}
    except Exception as e:
        raise HTTPException(400, str(e))
