import random
import datetime
from CRUD import RequeteSQL

# --- Données pour la génération aléatoire ---
NOMS = ["Dupont", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre"]
PRENOMS = ["Jean", "Pierre", "Paul", "Marie", "Sophie", "Julie", "Thomas", "Nicolas", "Julien", "Antoine", "Lucas", "Camille", "Manon"]
RUES = ["Route de l'Aviation", "Chemin des Nuages", "Rue Eole", "Avenue Icare", "Impasse du Kérosène", "Boulevard du Pilote"]
TYPES_AVIONS = ["Piper PA-28", "Cessna 172", "Robin DR400", "Diamond DA40", "Cirrus SR20"]
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
    h = random.randint(6, 22)
    m = random.randint(0, 59)
    return f"{h:02d}:{m:02d}"

# --- Script Principal ---

def main():
    print("Connexion à la base de données...")
    db = RequeteSQL("Aerodrome.db")

    # NOTE : Si tu veux vider la base avant de remplir, tu peux décommenter les lignes Delete
    # db.Delete("Remplir", "1=1") # 1=1 est une astuce pour dire "Toujours vrai" -> Tout supprimer
    # ...

    print("--- Création des données statiques ---")
    
    # 1. Carburants
    try:
        for c in CARBURANTS:
            # Type_carburant, prix_litre, Quantite_max
            db.Insert("Carburant", [c[0], c[1], c[2]])
    except Exception:
        pass 

    # 2. Infrastructures (Parking & Hangar)
    nb_parkings = 30
    print(f"Création de {nb_parkings} places de parking...")
    for i in range(1, nb_parkings + 1):
        try:
            prix_code = 'A' if i < 10 else 'B'
            db.Insert("Parking", [i, "Standard", prix_code])
        except: pass

    nb_hangars = 10
    print(f"Création de {nb_hangars} hangars...")
    for i in range(1, nb_hangars + 1):
        try:
            db.Insert("Hangar", [i, "Large", 50, 300, 1000])
        except: pass

    # 3. Création des Humains et Comptes
    print("--- Création du Gestionnaire, Agents et Pilotes ---")
    
    # A. Le Gestionnaire (Unique)
    try:
        identifiant_gest = "admin"
        mdp_gest = "superadmin"
        db.Insert("Compte", [identifiant_gest, mdp_gest])
        # id_gestionnaire, Nom, Prenom, Adresse, Telephone, identifiant
        db.Insert("Gestionnaire_Aerodrome", [1, "Directeur", "Grand", "Tour de Contrôle", generer_telephone(), identifiant_gest])
        print("Gestionnaire créé.")
    except:
        print("Le gestionnaire existe déjà.")

    # B. Les Agents
    agent_ids = []
    for i in range(1, 6):
        identifiant = f"agent{i}"
        mdp = "admin123"
        try:
            db.Insert("Compte", [identifiant, mdp])
            nom = random.choice(NOMS)
            prenom = random.choice(PRENOMS)
            db.Insert("AgentExploitation", [i, nom, prenom, random.choice(RUES), generer_telephone(), identifiant])
            agent_ids.append(i)
        except: 
            agent_ids.append(i)

    # C. Les Pilotes
    pilote_ids = []
    for i in range(1, 31):
        identifiant = f"pilote{i}"
        mdp = "voler123"
        try:
            db.Insert("Compte", [identifiant, mdp])
            nom = random.choice(NOMS)
            prenom = random.choice(PRENOMS)
            db.Insert("Pilote", [i, nom, prenom, random.choice(RUES), generer_telephone(), identifiant])
            pilote_ids.append(i)
        except:
            pilote_ids.append(i)

    # 4. Création des Avions
    print("--- Création des Avions ---")
    avion_ids = []
    for i in range(1, 41): # 40 avions
        try:
            modele = random.choice(TYPES_AVIONS)
            capa = 200 if "Da40" in modele else 140 
            proprio = random.choice(pilote_ids)
            db.Insert("Avion", [i, modele, capa, proprio])
            avion_ids.append(i)
        except:
            avion_ids.append(i)

    # 5. Génération massive
    print("--- Génération des Réservations et données liées ---")
    
    nb_reservations = 250 
    
    for i in range(1, nb_reservations + 1):
        try:
            # A. Créer un Vol
            id_vol = i
            h_dep = generer_heure()
            h_arr = generer_heure() 
            db.Insert("Vol", [id_vol, h_dep, h_arr])

            # B. Créer une Facture
            id_facture = i
            recette = random.randint(100, 500)
            agent_responsable = random.choice(agent_ids)
            db.Insert("Facture", [id_facture, recette, recette*30, recette*365, recette, agent_responsable])

            # C. Créer la Réservation
            id_resa = i
            id_avion = random.choice(avion_ids)
            id_parking = random.randint(1, nb_parkings)
            date_resa = generer_date_future()
            etat = random.choice(["Confirmée", "En attente", "Terminée"])
            
            db.Insert("Reservation", [id_resa, etat, date_resa, "Non", id_vol, id_avion, id_parking, id_facture])

            # D. Remplir du carburant (1 fois sur 2)
            if random.random() > 0.5:
                type_carb = "AVGAS 100LL" 
                if i % 10 == 0: type_carb = "JET A1"
                quantite = random.randint(20, 100)
                db.Insert("Remplir", [id_resa, quantite, type_carb])

        except Exception as e:
            pass

    print("Terminé ! La base de données a été peuplée (y compris le Gestionnaire).")
    db.CloseDB()

if __name__ == "__main__":
    main()