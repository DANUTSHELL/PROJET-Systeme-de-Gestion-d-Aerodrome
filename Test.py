import random
import datetime
from CRUD import RequeteSQL

# --- Données Aléatoires ---
NOMS = ["Dupont", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Moneger", "Ansari", "Guerin", "Boyer", "Garnier", "Chevalier"]
PRENOMS = ["Jean", "Pierre", "Paul", "Marie", "Sophie", "Julie", "Thomas", "Nicolas", "Julien", "Antoine", "Lucas", "Camille", "Manon", "Lea", "Alexandre", "Laura", "Sarah", "Kevin", "Enzo", "Mathis", "Emma", "Chloe"]
RUES = ["Route de l'Aviation", "Chemin des Nuages", "Rue Eole", "Avenue Icare", "Impasse du Kérosène", "Boulevard du Pilote", "Allée des Hélices", "Rue du Tarmac", "Impasse du Cockpit", "Voie des Airs"]
TYPES_AVIONS = ["Piper PA-28", "Cessna 172", "Robin DR400", "Diamond DA40", "Cirrus SR20", "Beechcraft Bonanza"]

CARBURANTS = [("AVGAS 100LL", 2.35, 10000), ("JET A1", 1.85, 25000)]

def get_phone():
    return f"06{random.randint(10000000, 99999999)}"

def get_date():
    start_date = datetime.date.today()
    return (start_date + datetime.timedelta(days=random.randint(1, 365))).strftime("%d/%m/%Y")

def get_time():
    return f"{random.randint(6, 21):02d}:{random.randint(0, 59):02d}"

def main():
    print("--- Démarrage du peuplement de la BDD ---")
    db = RequeteSQL("Aerodrome.db")

    # 1. Carburants & Infrastructures
    print("1. Création Infrastructures...")
    for c in CARBURANTS:
        try: db.Insert("Carburant", [c[0], c[1], c[2]])
        except: pass
    
    parking_ids = []
    for i in range(30): # 30 Parkings
        db.Insert("Parking", [None, "Standard", 'A' if i<10 else 'B'])
        parking_ids.append(db.cur.lastrowid)

    hangar_ids = []
    for i in range(10): # 10 Hangars
        db.Insert("Hangar", [None, "Large", 50, 300, 1000])
        hangar_ids.append(db.cur.lastrowid)

    # 2. Utilisateurs (Comptes + Rôles)
    print("2. Création Utilisateurs...")
    
    # Gestionnaire
    try:
        db.Insert("Compte", ["admin", "pass", "Gestionnaire"])
        db.Insert("Gestionnaire_Aerodrome", [None, "Boss", "Big", "Bureau", get_phone(), "admin"])
    except: pass

    # Agents (5)
    agent_ids = []
    for i in range(1, 6):
        uid = f"agent{i}"
        try:
            db.Insert("Compte", [uid, "1234", "Agent"])
            db.Insert("AgentExploitation", [None, random.choice(NOMS), random.choice(PRENOMS), random.choice(RUES), get_phone(), uid])
            agent_ids.append(db.cur.lastrowid)
        except: pass

    # Pilotes (40)
    pilote_ids = []
    for i in range(1, 41):
        uid = f"pilote{i}"
        try:
            db.Insert("Compte", [uid, "1234", "Pilote"])
            db.Insert("Pilote", [None, random.choice(NOMS), random.choice(PRENOMS), random.choice(RUES), get_phone(), uid])
            pilote_ids.append(db.cur.lastrowid)
        except: pass

    # 3. Avions
    print("3. Création Avions...")
    avion_ids = []
    if pilote_ids:
        for i in range(50):
            try:
                modele = random.choice(TYPES_AVIONS)
                db.Insert("Avion", [None, modele, 150, random.choice(pilote_ids)])
                avion_ids.append(db.cur.lastrowid)
            except: pass

    # 4. Flux massif (Vols, Factures, Résas)
    print("4. Génération massive des opérations...")
    
    NB_LOOPS = 400 # 400 * 3 tables = 1200 enregistrements minimum
    
    for i in range(NB_LOOPS):
        try:
            # A. Vol
            db.Insert("Vol", [None, get_time(), get_time()])
            id_vol = db.cur.lastrowid
            
            # B. Facture (Peut être vide au début, ou pré-remplie)
            recette = random.randint(50, 800)
            id_ag = random.choice(agent_ids) if agent_ids else 1
            # id, r_jour, r_mois, r_annee, total, id_agent
            db.Insert("Facture", [None, recette, recette, recette, recette, id_ag])
            id_fact = db.cur.lastrowid
            
            # C. Réservation
            etat = random.choice(["Demandé", "Confirmée", "Achevée", "Annulée"])
            dispo = "Oui" if etat in ["Confirmée", "Achevée"] else "Non"
            id_av = random.choice(avion_ids)
            id_pk = random.choice(parking_ids)
            
            # id, Etat, Date, Dispo, id_vol, id_avion, id_parking, id_facture
            db.Insert("Reservation", [None, etat, get_date(), dispo, id_vol, id_av, id_pk, id_fact])
            id_resa = db.cur.lastrowid
            
            # D. Services aléatoires
            # Carburant (1 fois sur 3)
            if random.random() > 0.66:
                db.Insert("Remplir", [id_resa, random.randint(20, 100), "AVGAS 100LL"])
            
            # Hangar (1 fois sur 10)
            if random.random() > 0.9:
                db.Insert("Emplacement", [None, id_resa, random.choice(hangar_ids)])
                
        except Exception as e:
            # print(f"Erreur itération {i}: {e}")
            pass

    # 5. Messages
    print("5. Envoi de messages...")
    for _ in range(50):
        try:
            db.Insert("Message", [random.choice(agent_ids), random.choice(pilote_ids), "Message test de système."])
        except: pass

    db.CloseDB()
    print("---------------------------------------")
    print(f"TERMINÉ ! Base de données peuplée avec ~{NB_LOOPS*3 + 100} entrées.")

if __name__ == "__main__":
    main()