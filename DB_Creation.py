import sqlite3

def init_db():
    print("Réinitialisation de la base de données...")
    con = sqlite3.connect("Aerodrome.db")
    cur = con.cursor()

    # On active les Foreign Keys
    cur.execute("PRAGMA foreign_keys = ON;")

    # Nettoyage préalable (Ordre important pour ne pas casser les liens)
    tables = ["Remplir", "Message", "Emplacement", "Reservation", "Facture", 
              "Vol", "Parking", "Hangar", "Carburant", "Avion", 
              "Pilote", "Gestionnaire_Aerodrome", "AgentExploitation", "Compte"]
    
    for t in tables:
        cur.execute(f"DROP TABLE IF EXISTS {t}")

    # Création du schéma
    cur.executescript("""
        -- 1. Table COMPTE (Centrale pour l'authentification)
        CREATE TABLE Compte (
             identifiant varchar(255) not null,
             Mot_de_passe varchar(255) not null,
             Role varchar(50) not null, -- 'Pilote', 'Agent', 'Gestionnaire'
             PRIMARY KEY (identifiant)
        );

        -- 2. Tables des ROLES
        CREATE TABLE AgentExploitation (
             id_agent INTEGER PRIMARY KEY AUTOINCREMENT,
             Nom varchar(30) not null,
             Prenom varchar(30) not null,
             Adresse varchar(255),
             Telephone varchar(13),
             identifiant varchar(255) not null,
             FOREIGN KEY (identifiant) REFERENCES Compte(identifiant)
        );

        CREATE TABLE Gestionnaire_Aerodrome (
             id_gestionnaire INTEGER PRIMARY KEY AUTOINCREMENT,
             Nom varchar(30) not null,
             Prenom varchar(30) not null,
             Adresse varchar(255),
             Telephone varchar(13),
             identifiant varchar(255) not null,
             FOREIGN KEY (identifiant) REFERENCES Compte(identifiant)
        );

        CREATE TABLE Pilote (
             id_pilote INTEGER PRIMARY KEY AUTOINCREMENT,
             Nom varchar(30) not null,
             Prenom varchar(30) not null,
             Adresse varchar(255),
             Telephone varchar(13),
             identifiant varchar(255) not null,
             FOREIGN KEY (identifiant) REFERENCES Compte(identifiant)
        );

        -- 3. Ressources Matérielles
        CREATE TABLE Avion (
             id_avion INTEGER PRIMARY KEY AUTOINCREMENT,
             TypeAvion varchar(20) not null,
             Capacite_carburant numeric(3) not null,
             id_pilote INTEGER not null,
             FOREIGN KEY (id_pilote) REFERENCES Pilote(id_pilote)
        );

        CREATE TABLE Carburant (
             Type_carburant varchar(30) not null,
             prix_litre float(10) not null,
             Quantite_max numeric(10) not null,
             PRIMARY KEY (Type_carburant)
        );

        CREATE TABLE Hangar (
             id_hangar INTEGER PRIMARY KEY AUTOINCREMENT,
             Taille varchar(10) not null,
             Prix_jour numeric(10) not null,
             Prix_semaine numeric(10) not null,
             Prix_mois numeric(10) not null
        );

        CREATE TABLE Parking (
             id_parking INTEGER PRIMARY KEY AUTOINCREMENT,
             Taille varchar(10) not null,
             Prix char(1) not null
        );
        
        -- 4. Opérations
        CREATE TABLE Vol (
             id_vol INTEGER PRIMARY KEY AUTOINCREMENT,
             Heure_depart varchar(10),
             Heure_arrivee varchar(10)
        );

        CREATE TABLE Facture (
             id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
             r_jour numeric(10,2) DEFAULT 0,
             r_mois numeric(10,2) DEFAULT 0,
             r_annee numeric(10,2) DEFAULT 0,
             total numeric(10,2) DEFAULT 0,
             id_agent INTEGER, -- Peut être NULL si facture auto-générée sans agent assigné au début
             FOREIGN KEY (id_agent) REFERENCES AgentExploitation(id_agent)
        );

        -- Correction Cohérence : Les FK peuvent être NULL pour une simple demande
        CREATE TABLE Reservation (
             id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
             Etat varchar(30) not null, -- 'Demandé', 'Confirmée', 'Annulée'
             Date varchar(10) not null,
             Dispo varchar(10) DEFAULT 'Non',
             id_vol INTEGER,
             id_avion INTEGER not null,
             id_parking INTEGER,
             id_facture INTEGER,
             FOREIGN KEY (id_vol) REFERENCES Vol(id_vol),
             FOREIGN KEY (id_avion) REFERENCES Avion(id_avion),
             FOREIGN KEY (id_parking) REFERENCES Parking(id_parking),
             FOREIGN KEY (id_facture) REFERENCES Facture(id_facture)
        );

        CREATE TABLE Emplacement (
             num_emplacement INTEGER PRIMARY KEY AUTOINCREMENT,
             id_reservation INTEGER not null,
             id_hangar INTEGER not null,
             FOREIGN KEY (id_hangar) REFERENCES Hangar(id_hangar),
             FOREIGN KEY (id_reservation) REFERENCES Reservation(id_reservation)
        );

        CREATE TABLE Message (
             id_agent INTEGER not null,
             id_pilote INTEGER not null,
             Texte varchar(255) not null,
             PRIMARY KEY (id_agent, id_pilote), -- Une seule conversation active par paire
             FOREIGN KEY (id_pilote) REFERENCES Pilote(id_pilote),
             FOREIGN KEY (id_agent) REFERENCES AgentExploitation(id_agent)
        );

        CREATE TABLE Remplir (
             id_reservation INTEGER not null,
             Quantite numeric(10) not null,
             Type_carburant varchar(30) not null,
             PRIMARY KEY (id_reservation),
             FOREIGN KEY (id_reservation) REFERENCES Reservation(id_reservation),
             FOREIGN KEY (Type_carburant) REFERENCES Carburant(Type_carburant)
        );
    """)

    con.commit()
    con.close()
    print("Base de données créée avec succès (Structure corrigée).")

if __name__ == "__main__":
    init_db()