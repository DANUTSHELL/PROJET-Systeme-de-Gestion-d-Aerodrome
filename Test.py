import random
import datetime
from CRUD import RequeteSQL

# --- Listes de données pour la génération aléatoire ---
NOMS = ["Dupont", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Moneger", "Ansari"]
PRENOMS = ["Jean", "Pierre", "Paul", "Marie", "Sophie", "Julie", "Thomas", "Nicolas", "Julien", "Antoine", "Lucas", "Camille", "Manon", "Lea", "Alexandre", "Laura", "Sarah", "Kevin"]
RUES = ["Route de l'Aviation", "Chemin des Nuages", "Rue Eole", "Avenue Icare", "Impasse du Kérosène", "Boulevard du Pilote", "Allée des Hélices", "Rue du Tarmac"]

# Avions cohérents pour un aéroclub privé
TYPES_AVIONS = ["Piper PA-28", "Cessna 172", "Robin DR400", "Diamond DA40", "Cirrus SR20"]

# Carburants fixes (Tuple: Nom, Prix, Stock Max)
CARBURANTS = [
    ("AVGAS 100LL", 2.35, 10000), 
    ("JET A1", 1.85, 25000)
]

def generer_telephone():
    return f"06{random.randint(10000000, 99999999)}"

def generer_date_future():
    start_date = datetime.date.today()
    random_days = random.randint(1, 365)
    date = start_date + datetime.timedelta(days=random_days)
    return date.strftime("%d/%m/%Y")

def generer_heure():
    h = random.randint(6, 21) # Vols entre 06h et 21h
    m = random.randint(0, 59)
    return f"{h:02d}:{m:02d}"

def main():
    print("------------------------------------------------")
    print("Initialisation de la génération de données...")
    print("Connexion à Aerodrome.db...")
    
    # Instance de la classe CRUD
    db = RequeteSQL("Aerodrome.db")
    
    # Note : On ne vide pas la base ici par sécurité, 
    # mais assure-toi d'avoir une base vide (via Creation_DB.py) avant de lancer ce script.

    # ---------------------------------------------------------
    # 1. DONNÉES STATIQUES (Carburant, Infra)
    # ---------------------------------------------------------
    print("-> Insertion des carburants et infrastructures...")
    
    # Carburants
    try:
        for c in CARBURANTS:
            # Type_carburant, prix_litre, Quantite_max
            db.Insert("Carburant", [c[0], c[1], c[2]])
    except: pass 

    # Parkings (30 places)
    parkings_ids = []
    for i in range(1, 31):
        try:
            # id (auto -> None), Taille, Prix
            # Prix 'A' (couvert) ou 'B' (extérieur)
            prix_code = 150 if i < 10 else 50
            db.Insert("Parking", [None, "Standard", prix_code])
            parkings_ids.append(db.cur.lastrowid)
        except: pass

    # Hangars (10 hangars)
    hangars_ids = []
    for i in range(1, 11):
        try:
            # id (auto), Taille, Prix_j, Prix_s, Prix_m
            db.Insert("Hangar", [None, "Large", 50, 300, 1000])
            hangars_ids.append(db.cur.lastrowid)
        except: pass

    # ---------------------------------------------------------
    # 2. HUMAINS & COMPTES (Avec la nouvelle colonne ROLE)
    # ---------------------------------------------------------
    print("-> Création des comptes (Gestionnaire, Agents, Pilotes)...")

    # A. Le Gestionnaire (Unique)
    try:
        identifiant_gest = "admin"
        # Table Compte : identifiant, Mot_de_passe, Role
        db.Insert("Compte", [identifiant_gest, "superadmin", "Gestionnaire"])
        
        # Table Gestionnaire : id (auto), Nom, Prenom, Adresse, Tel, identifiant
        db.Insert("Gestionnaire_Aerodrome", [None, "Directeur", "Grand", "Tour de Contrôle", generer_telephone(), identifiant_gest])
    except Exception as e:
        # print(f"Info: Gestionnaire existe déjà ou erreur: {e}")
        pass

    # B. Les Agents (5 agents)
    agent_ids = []
    for i in range(1, 6):
        identifiant = f"agent{i}"
        try:
            # 1. Compte
            db.Insert("Compte", [identifiant, "admin123", "Agent"])
            
            # 2. Profil Agent
            nom = random.choice(NOMS)
            prenom = random.choice(PRENOMS)
            db.Insert("AgentExploitation", [None, nom, prenom, random.choice(RUES), generer_telephone(), identifiant])
            
            # On récupère l'ID généré automatiquement pour l'utiliser dans les factures plus tard
            agent_ids.append(db.cur.lastrowid)
        except: 
            pass

    # C. Les Pilotes (40 pilotes)
    pilote_ids = []
    for i in range(1, 41):
        identifiant = f"pilote{i}"
        try:
            # 1. Compte
            db.Insert("Compte", [identifiant, "voler123", "Pilote"])
            
            # 2. Profil Pilote
            nom = random.choice(NOMS)
            prenom = random.choice(PRENOMS)
            db.Insert("Pilote", [None, nom, prenom, random.choice(RUES), generer_telephone(), identifiant])
            
            pilote_ids.append(db.cur.lastrowid)
        except:
            pass

    # ---------------------------------------------------------
    # 3. AVIONS
    # ---------------------------------------------------------
    print("-> Création de la flotte d'avions...")
    avion_ids = []
    
    if pilote_ids: # On vérifie qu'on a des pilotes
        for i in range(1, 51): # 50 avions
            try:
                modele = random.choice(TYPES_AVIONS)
                # Capacité carburant dépend du modèle (simplifié)
                capa = 200 if "DA40" in modele else 140 
                proprio_id = random.choice(pilote_ids)
                
                # Table Avion: id(auto), Type, Capa, id_pilote
                db.Insert("Avion", [None, modele, capa, proprio_id])
                avion_ids.append(db.cur.lastrowid)
            except:
                pass

    # ---------------------------------------------------------
    # 4. GÉNÉRATION MASSIVE (Vols, Réservations, Factures)
    # ---------------------------------------------------------
    print("-> Génération massive des opérations (Vols, Factures, Réservations)...")
    
    # On va générer environ 350 boucles.
    # Chaque boucle crée 1 Vol + 1 Facture + 1 Réservation (+ parfois Carburant/Hangar)
    # Total ~ 1000 à 1500 enregistrements dans la base.
    
    NB_OPERATIONS = 350
    
    for i in range(NB_OPERATIONS):
        try:
            # A. Créer un Vol
            h_dep = generer_heure()
            h_arr = generer_heure() 
            # id(auto), Heure_depart, Heure_arrivee
            db.Insert("Vol", [None, h_dep, h_arr])
            id_vol_cree = db.cur.lastrowid

            # B. Créer une Facture
            recette = random.randint(80, 600)
            id_agent_resp = random.choice(agent_ids) if agent_ids else 1
            
            # id(auto), r_jour, r_mois, r_annee, total, id_agent
            # Note: Pour simplifier, on met le total partout, le reporting fera les sommes
            db.Insert("Facture", [None, recette, recette, recette, recette, id_agent_resp])
            id_facture_cree = db.cur.lastrowid

            # C. Créer la Réservation
            id_avion_concerne = random.choice(avion_ids) if avion_ids else 1
            id_parking_concerne = random.choice(parkings_ids) if parkings_ids else 1
            date_resa = generer_date_future()
            etat = random.choice(["Confirmée", "Terminée", "En attente"])
            dispo = "Oui" if etat != "En attente" else "Non"
            
            # id(auto), Etat, Date, Dispo, id_vol, id_avion, id_parking, id_facture
            db.Insert("Reservation", [
                None, 
                etat, 
                date_resa, 
                dispo, 
                id_vol_cree, 
                id_avion_concerne, 
                id_parking_concerne, 
                id_facture_cree
            ])
            id_resa_cree = db.cur.lastrowid

            # D. Optionnel : Remplir du carburant (1 fois sur 3)
            if random.random() > 0.6:
                type_carb = "AVGAS 100LL" 
                # Les jets prennent du JET A1
                if "DA40" in str(id_avion_concerne): type_carb = "JET A1" # Simplification
                
                qty = random.randint(30, 120)
                # id_reservation, Quantite, Type_carburant
                db.Insert("Remplir", [id_resa_cree, qty, type_carb])

            # E. Optionnel : Louer un emplacement Hangar (1 fois sur 10)
            if random.random() > 0.9 and hangars_ids:
                id_hangar = random.choice(hangars_ids)
                # num_emplacement(auto), id_reservation, id_hangar
                db.Insert("Emplacement", [None, id_resa_cree, id_hangar])

        except Exception as e:
            # print(f"Erreur boucle {i}: {e}")
            pass

    # ---------------------------------------------------------
    # 5. MESSAGERIE (Quelques messages aléatoires)
    # ---------------------------------------------------------
    print("-> Génération des messages...")
    for _ in range(50):
        try:
            ag = random.choice(agent_ids)
            pil = random.choice(pilote_ids)
            textes = ["Besoin de confirmation pour demain", "Vol annulé cause météo", "Facture reçue ?", "Pouvez-vous valider mon créneau ?", "Parking 4 libéré"]
            msg = random.choice(textes)
            
            # id_agent, id_pilote, Texte
            db.Insert("Message", [ag, pil, msg])
        except:
            pass # Doublon de clé primaire (agent, pilote) probable, on ignore

    db.CloseDB()
    print("------------------------------------------------")
    print("TERMINÉ ! Base de données 'Aerodrome.db' remplie avec succès.")
    print(f"Environ {NB_OPERATIONS} vols/réservations générés.")

if __name__ == "__main__":
    main()