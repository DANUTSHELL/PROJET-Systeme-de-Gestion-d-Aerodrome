import sqlite3

con = sqlite3.connect("Aerodrome.db")
cur = con.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

cur.executescript("""

    CREATE TABLE IF NOT EXISTS Compte (
         identifiant varchar(255) not null,
         Mot_de_passe varchar(255) not null,
         Role varchar(255) not null,
         PRIMARY KEY (identifiant)
    );

    CREATE TABLE IF NOT EXISTS AgentExploitation (
         id_agent INTEGER PRIMARY KEY AUTOINCREMENT,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         FOREIGN KEY (identifiant) REFERENCES Compte(identifiant)
    );

    CREATE TABLE IF NOT EXISTS Gestionnaire_Aerodrome (
         id_gestionnaire INTEGER PRIMARY KEY AUTOINCREMENT,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         FOREIGN KEY (identifiant) REFERENCES Compte(identifiant)
    );

    CREATE TABLE IF NOT EXISTS Pilote (
         id_pilote INTEGER PRIMARY KEY AUTOINCREMENT,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         FOREIGN KEY (identifiant) REFERENCES Compte(identifiant)
    );

    CREATE TABLE IF NOT EXISTS Avion (
         id_avion INTEGER PRIMARY KEY AUTOINCREMENT,
         TypeAvion varchar(20) not null,
         Capacite_carburant numeric(3) not null,
         id_pilote INTEGER not null,
         FOREIGN KEY (id_pilote) REFERENCES Pilote(id_pilote)
    );

    CREATE TABLE IF NOT EXISTS Carburant (
         Type_carburant varchar(30) not null,
         prix_litre float(10) not null,
         Quantite_max numeric(10) not null,
         PRIMARY KEY (Type_carburant)
    );

    CREATE TABLE IF NOT EXISTS Hangar (
         id_hangar INTEGER PRIMARY KEY AUTOINCREMENT,
         Taille varchar(10) not null,
         Prix_jour numeric(10) not null,
         Prix_semaine numeric(10) not null,
         Prix_mois numeric(10) not null
    );

    CREATE TABLE IF NOT EXISTS Parking (
         id_parking INTEGER PRIMARY KEY AUTOINCREMENT,
         Taille varchar(10) not null,
         Prix char(1) not null
    );
    

    CREATE TABLE IF NOT EXISTS Vol (
         id_vol INTEGER PRIMARY KEY AUTOINCREMENT,
         Heure_depart varchar(10) not null,
         Heure_arrivee varchar(10) not null
    );

    CREATE TABLE IF NOT EXISTS Facture (
         id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
         r_jour numeric(100) not null,
         r_mois numeric(100) not null,
         r_annee numeric(100) not null,
         total numeric(100) not null,
         id_agent INTEGER not null,
         FOREIGN KEY (id_agent) REFERENCES AgentExploitation(id_agent)
    );

    CREATE TABLE IF NOT EXISTS Reservation (
         id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
         Etat varchar(30) not null,
         Date varchar(10) not null,
         Dispo varchar(10) not null,
         id_vol INTEGER,
         id_avion INTEGER not null,
         id_parking INTEGER,
         id_facture INTEGER not null,
         FOREIGN KEY (id_vol) REFERENCES Vol(id_vol),
         FOREIGN KEY (id_avion) REFERENCES Avion(id_avion),
         FOREIGN KEY (id_parking) REFERENCES Parking(id_parking),
         FOREIGN KEY (id_facture) REFERENCES Facture(id_facture)
    );

    CREATE TABLE IF NOT EXISTS Emplacement (
         num_emplacement INTEGER PRIMARY KEY AUTOINCREMENT,
         id_reservation INTEGER not null,
         id_hangar INTEGER not null,
         FOREIGN KEY (id_hangar) REFERENCES Hangar(id_hangar),
         FOREIGN KEY (id_reservation) REFERENCES Reservation(id_reservation)
    );

    CREATE TABLE IF NOT EXISTS Message (
         id_agent INTEGER not null,
         id_pilote INTEGER not null,
         Texte varchar(255) not null,
         PRIMARY KEY (id_agent, id_pilote),
         FOREIGN KEY (id_pilote) REFERENCES Pilote(id_pilote),
         FOREIGN KEY (id_agent) REFERENCES AgentExploitation(id_agent)
    );

    CREATE TABLE IF NOT EXISTS Remplir (
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