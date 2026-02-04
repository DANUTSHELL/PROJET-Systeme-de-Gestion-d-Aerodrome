from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Literal
from CRUD import RequeteSQL
from datetime import datetime

# ==========================================
# 1. INITIALISATION
# ==========================================
app = FastAPI(
    title="Système de Gestion d'Aérodrome",
    description="API pour Agent d'Exploitation et Gestionnaire",
    version="Final-RoleBased"
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

class UpdatePrixCarburant(BaseModel):
    type_carburant: str
    nouveau_prix: float

class NouveauHangar(BaseModel):
    Taille: str
    Prix_jour: float
    Prix_semaine: float
    Prix_mois: float

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

@app.post("/pilotes/inscription")
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
        # On récupère le compte pour le supprimer aussi
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
        dispo = "Oui" if validation.decision != "Annulée" else "Non"
        db.Update("Reservation", "Dispo", dispo, f"id_reservation={id_resa}")
        return {"message": f"Créneau {id_resa} passé à {validation.decision}"}
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
        
        park = db.Select("Parking", f"id_parking={id_parking}")
        if park:
            code_prix = park[0][2]
            total += 50.0 if code_prix == 'A' else 20.0
            
        # 3. Coût Carburant
        remplir = db.Select("Remplir", f"id_reservation={id_reservation}")
        if remplir:
            qte = remplir[0][1]
            type_c = remplir[0][2]
            carb_info = db.Select("Carburant", f"Type_carburant='{type_c}'")
            if carb_info:
                prix_L = carb_info[0][1]
                total += (qte * prix_L)

        db.Update("Facture", "total", total, f"id_facture={id_facture}")
        db.Update("Facture", "id_agent", id_agent, f"id_facture={id_facture}")
        
        db.Update("Facture", "r_jour", total, f"id_facture={id_facture}")
        db.Update("Facture", "r_mois", total, f"id_facture={id_facture}")
        db.Update("Facture", "r_annee", total, f"id_facture={id_facture}")

        return {"message": "Facture générée", "Total_Calculé": total, "id_facture": id_facture}

    except Exception as e:
        raise HTTPException(400, str(e))


# ==========================================
# 6. ESPACE GESTIONNAIRE D'AÉRODROME
# ==========================================

TAG_GEST = "Gestionnaire d'Aérodrome"

# --- A. VISUALISER LE FLUX DES MOUVEMENTS ---

@app.get("/gestionnaire/flux", tags=[TAG_GEST])
def visualiser_flux(role: str = Query(..., description="Doit être 'Gestionnaire'")):
    """
    1. Visualiser le flux des mouvements par état.
    """
    verifier_role("Gestionnaire", role)
    try:
        all_resas = db.Select("Reservation")
        stats = {
            "En attente (Demandé)": 0,
            "Confirmée": 0,
            "Autorisée": 0,
            "Achevée": 0,
            "Annulée": 0,
            "Total": 0
        }
        
        for r in all_resas:
            etat = r[1]
            if etat in stats:
                stats[etat] += 1
            else:
                stats[etat] = 1
            stats["Total"] += 1
            
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
        "Hangars_Dispo": len(hangars),
        "Parkings_Dispo": len(parkings)
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
    """
    3. Suivi des recettes journalières, mensuelles, annuelles.
    4. Générer un rapport complet.
    """
    verifier_role("Gestionnaire", role)
    try:
        factures = db.Select("Facture")
        
        recette_totale = 0
        nb_factures = 0
        
        for f in factures:
            recette_totale += f[4] # Total
            nb_factures += 1
            
        rapport = {
            "Date_Generation": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Volume_Ventes": nb_factures,
            "Recettes_Globales": recette_totale,
            "Analyse_Temporelle": {
                "Recette_Journaliere_Estimee": recette_totale / 365, # Moyenne simple
                "Recette_Mensuelle_Estimee": recette_totale / 12,
                "Recette_Annuelle_Reelle": recette_totale
            },
            "Conclusion": "Situation financière stable." if recette_totale > 0 else "Aucune recette enregistrée."
        }
        return rapport
    except Exception as e:
        raise HTTPException(500, str(e))


# ==========================================
# 7. ESPACE PILOTE
# ==========================================

@app.post("/pilote/demande_creneau", tags=["Pilote"])
def demander_creneau_pilote(demande: DemandeCreneauModel):
    try:
        # --- 1. VÉRIFICATION AUTOMATIQUE DE DISPONIBILITÉ ---
        
        condition = f"Date = '{demande.date_souhaitee}' AND id_parking = {demande.id_parking_souhaite} AND Etat != 'Annulée'"
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
        
        # A. Création du Vol
        db.Insert("Vol", [None, demande.heure_depart, demande.heure_arrivee])
        id_vol = db.cur.lastrowid
        
        # B. Création de la Facture
        db.Insert("Facture", [None, 0, 0, 0, 0, 1]) 
        id_fac = db.cur.lastrowid
        
        # C. Création de la Réservation avec l'état CALCULÉ AUTOMATIQUEMENT
        db.Insert("Reservation", [
            None, 
            etat_auto,
            demande.date_souhaitee, 
            dispo_auto,
            id_vol, 
            demande.id_avion, 
            demande.id_parking_souhaite, 
            id_fac
        ])
        
        return {
            "message": message_retour, 
            "Etat_Attribué": etat_auto, 
            "Disponibilite_Systeme": dispo_auto,
            "id_reservation": db.cur.lastrowid
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/pilote/mes_factures", tags=["Pilote"])
def consulter_mes_factures(id_pilote: int, role: str = Query(..., description="Doit être 'Pilote'")):
    """
    Permet au pilote de voir l'historique de ses paiements.
    Logique : Pilote -> Ses Avions -> Les Réservations de ces avions -> Les Factures liées.
    """
    verifier_role("Pilote", role)
    
    try:
        # Étape 1 : Trouver tous les avions du pilote
        # Table Avion : id_avion(0), Type(1), Capa(2), id_pilote(3)
        avions = db.Select("Avion", f"id_pilote={id_pilote}")
        if not avions:
            return {"message": "Aucun avion, donc aucune facture."}
            
        ids_avions = [a[0] for a in avions] # Liste des ID d'avions (ex: [1, 5, 12])
        
        mes_factures = []

        # Étape 2 : Pour chaque avion, trouver les réservations
        for id_avion in ids_avions:
            # Table Reservation : ..., id_avion(5), ..., id_facture(7)
            resas = db.Select("Reservation", f"id_avion={id_avion}")
            
            for r in resas:
                id_facture = r[7] # Le lien vers la facture
                date_vol = r[2]   # La date du vol
                etat_resa = r[1]
                
                # Étape 3 : Récupérer les détails de la facture
                # Table Facture : id(0), r_jour(1), r_mois(2), r_annee(3), total(4), id_agent(5)
                fact_data = db.Select("Facture", f"id_facture={id_facture}")
                
                if fact_data:
                    f = fact_data[0]
                    montant = f[4]
                    
                    # Petite logique pour l'affichage du statut de paiement
                    statut_paiement = "En attente"
                    if montant > 0:
                        statut_paiement = "Traitée / À payer"
                    if etat_resa == "Annulée":
                        statut_paiement = "Annulée"

                    mes_factures.append({
                        "Reference_Facture": f[0],
                        "Date_Concernee": date_vol,
                        "Montant_Total": montant,
                        "Avion_Concerne": id_avion,
                        "Statut": statut_paiement
                    })
        
        return mes_factures

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))