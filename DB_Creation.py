import sqlite3

con = sqlite3.connect("Aerodrome.db")
cur = con.cursor()

cur.execute("PRAGMA foreign_keys = ON;")

cur.executescript("""
    create table if not exists Compte (
         identifiant varchar(255) not null,
         Mot_de_passe varchar(255) not null,
         primary key (identifiant)
    );

    create table if not exists AgentExploitation (
         id_agent INTEGER PRIMARY KEY AUTOINCREMENT,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         foreign key (identifiant) references Compte(identifiant)
    );

    create table if not exists Gestionnaire_Aerodrome (
         id_gestionnaire INTEGER PRIMARY KEY AUTOINCREMENT,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         foreign key (identifiant) references Compte(identifiant)
    );

    create table if not exists Pilote (
         id_pilote INTEGER PRIMARY KEY AUTOINCREMENT,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         foreign key (identifiant) references Compte(identifiant)
    );

    create table if not exists Avion (
         id_avion INTEGER PRIMARY KEY AUTOINCREMENT,
         TypeAvion varchar(20) not null,
         Capacite_carburant numeric(3) not null,
         id_pilote INTEGER not null,
         foreign key (id_pilote) references Pilote(id_pilote)
    );

    create table if not exists Carburant (
         Type_carburant varchar(30) not null,
         prix_litre float(10) not null,
         Quantite_max numeric(10) not null,
         primary key (Type_carburant)
    );

    create table if not exists Hangar (
         id_hangar INTEGER PRIMARY KEY AUTOINCREMENT,
         Taille varchar(10) not null,
         Prix_jour numeric(10) not null,
         Prix_semaine numeric(10) not null,
         Prix_mois numeric(10) not null
    );

    create table if not exists Parking (
         id_parking INTEGER PRIMARY KEY AUTOINCREMENT,
         Taille varchar(10) not null,
         Prix char(1) not null
    );
    
    create table if not exists Vol (
         id_vol INTEGER PRIMARY KEY AUTOINCREMENT,
         Heure_depart varchar(10) not null,
         Heure_arrivee varchar(10) not null
    );

    create table if not exists Facture (
         id_facture INTEGER PRIMARY KEY AUTOINCREMENT,
         r_jour numeric(100) not null,
         r_mois numeric(100) not null,
         r_annee numeric(100) not null,
         total numeric(100) not null,
         id_agent INTEGER not null,
         foreign key (id_agent) references AgentExploitation(id_agent)
    );

    create table if not exists Reservation (
         id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
         Etat varchar(30) not null,
         Date varchar(10) not null,
         Dispo varchar(10) not null,
         id_vol INTEGER,
         id_avion INTEGER not null,
         id_parking INTEGER,
         id_facture INTEGER not null,
         foreign key (id_vol) references Vol(id_vol),
         foreign key (id_avion) references Avion(id_avion),
         foreign key (id_parking) references Parking(id_parking),
         foreign key (id_facture) references Facture(id_facture)
    );

    create table if not exists Emplacement (
         num_emplacement INTEGER PRIMARY KEY AUTOINCREMENT,
         id_reservation INTEGER not null,
         id_hangar INTEGER not null,
         foreign key (id_hangar) references Hangar(id_hangar),
         foreign key (id_reservation) references Reservation(id_reservation)
    );

    create table if not exists Message (
         id_agent INTEGER not null,
         id_pilote INTEGER not null,
         Texte varchar(255) not null,
         primary key (id_agent, id_pilote),
         foreign key (id_pilote) references Pilote(id_pilote),
         foreign key (id_agent) references AgentExploitation(id_agent)
    );

    create table if not exists Remplir (
         id_reservation INTEGER not null,
         Quantite numeric(10) not null,
         Type_carburant varchar(30) not null,
         primary key (id_reservation),
         foreign key (id_reservation) references Reservation(id_reservation),
         foreign key (Type_carburant) references Carburant(Type_carburant)
    );
""")

con.commit()
con.close()
print("Base de données créée avec succès (Mode Auto-Incrément).")