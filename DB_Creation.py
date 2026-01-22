import sqlite3

con = sqlite3.connect("Aerodrome.db")
cur = con.cursor()

cur.executescript("""
    create table Compte (
         identifiant varchar(255) not null,
         Mot_de_passe varchar(255) not null,
         primary key (identifiant)
    );

    create table AgentExploitation (
         id_agent numeric(100) not null,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         primary key (id_agent)
         foreign key (identifiant) references Compte(identifiant)
    );

    create table Gestionnaire_Aerodrome (
         id_gestionnaire numeric(100) not null,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         primary key (id_gestionnaire),
         foreign key (identifiant) references Compte(identifiant)
    );

    create table Pilote (
         id_pilote numeric(100) not null,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         primary key (id_pilote),
         foreign key (identifiant) references Compte(identifiant)
    );

    create table Avion (
         id_avion numeric(100) not null,
         TypeAvion varchar(20) not null,
         Capacite_carburant numeric(3) not null,
         id_pilote numeric(100) not null,
         primary key (id_avion),
         foreign key (id_pilote) references Pilote(id_pilote)
    );

    create table Carburant (
         Type_carburant varchar(30) not null,
         prix_litre float(10) not null,
         Quantite_max numeric(10) not null,
         primary key (Type_carburant)
    );

    create table Hangar (
         id_hangar numeric(100) not null,
         Taille varchar(10) not null,
         Prix_jour numeric(10) not null,
         Prix_semaine numeric(10) not null,
         Prix_mois numeric(10) not null,
         primary key (id_hangar)
    );

    create table Parking (
         id_parking numeric(100) not null,
         Taille varchar(10) not null,
         Prix char(1) not null,
         primary key (id_parking)
    );
    
    create table Vol (
         id_vol numeric(100) not null,
         Heure_decollage varchar(10) not null,
         Heure_atterissage varchar(10) not null,
         primary key (id_vol)
    );

    create table Facture (
         id_facture numeric(100) not null,
         Recette_jour numeric(100) not null,
         Recette_mois numeric(100) not null,
         Recette_annee numeric(100) not null,
         Prix_Total numeric(100) not null,
         id_agent numeric(100) not null,
         primary key (id_facture),
         foreign key (id_agent) references AgentExploitation(id_agent)
    );

    create table Reservation (
         id_reservation numeric(100) not null,
         Etat varchar(30) not null,
         Date varchar(10) not null,
         Disponibilite varchar(10) not null,
         id_vol numeric(100),
         id_avion numeric(100) not null,
         id_parking numeric(100),
         id_facture numeric(100) not null,
         primary key (id_reservation),
         foreign key (id_vol) references Vol(id_vol),
         foreign key (id_avion) references Avion(id_avion),
         foreign key (id_parking) references Parking(id_parking),
         foreign key (id_facture) references Facture(id_facture)
    );

    create table Emplacement (
         num_emplacement numeric(100) not null,
         id_reservation numeric(100) not null,
         id_hangar numeric(100) not null,
         primary key (num_emplacement),
         foreign key (id_hangar) references Hangar(id_hangar),
         foreign key (id_reservation) references Reservation(id_reservation)
    );

    create table Message (
         id_agent numeric(100) not null,
         id_pilote numeric(100) not null,
         Texte varchar(255) not null,
         primary key (id_agent, id_pilote),
         foreign key (id_pilote) references Pilote(id_pilote),
         foreign key (id_agent) references AgentExploitation(id_agent)
    );

    create table Remplir (
         id_reservation numeric(100) not null,
         Quantite numeric(10) not null,
         Type_carburant varchar(30) not null,
         primary key (id_reservation),
         foreign key (id_reservation) references Reservation(id_reservation),
         foreign key (Type_carburant) references Carburant(Type_carburant)
    );
""")

con.commit()
con.close()