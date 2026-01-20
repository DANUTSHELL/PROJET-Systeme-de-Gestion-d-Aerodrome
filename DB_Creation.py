import sqlite3

con = sqlite3.connect("Aerodrome.db")
cur = con.cursor()

cur.executescript("""
    create table Compte (
         identifiant varchar(255) not null,
         Mot_de_passe varchar(255) not null,
         constraint ID_Compte_ID primary key (identifiant)
    );

    create table AgentExploitation (
         id_agent numeric(100) not null,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         constraint ID_AgentExploitation_ID primary key (id_agent),
         foreign key (identifiant) references Compte(identifiant)
    );

    create table Gestionnaire_Aerodrome (
         id_gestionnaire numeric(100) not null,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         constraint ID_Gestionnaire_Aerodrome_ID primary key (id_gestionnaire),
         foreign key (identifiant) references Compte(identifiant)
    );

    create table Pilote (
         id_pilote numeric(100) not null,
         Nom varchar(30) not null,
         Prenom varchar(30) not null,
         Adresse varchar(255) not null,
         Telephone varchar(13) not null,
         identifiant varchar(255) not null,
         constraint ID_Pilote_ID primary key (id_pilote),
         foreign key (identifiant) references Compte(identifiant)
    );

    create table Avion (
         id_avion numeric(100) not null,
         TypeAvion varchar(20) not null,
         Capacite_carburant numeric(3) not null,
         id_pilote numeric(100) not null,
         constraint ID_Avion_ID primary key (id_avion),
         foreign key (id_pilote) references Pilote(id_pilote)
    );

    create table Carburant (
         Type_carburant varchar(30) not null,
         prix_litre float(10) not null,
         Quantite_max numeric(10) not null,
         constraint ID_Carburant_ID primary key (Type_carburant)
    );

    create table Hangar (
         id_hangar numeric(100) not null,
         Taille varchar(10) not null,
         Prix_jour numeric(10) not null,
         Prix_semaine numeric(10) not null,
         Prix_mois numeric(10) not null,
         constraint ID_Hangar_ID primary key (id_hangar)
    );

    create table Parking (
         id_parking numeric(100) not null,
         Taille varchar(10) not null,
         Prix char(1) not null,
         constraint ID_Parking_ID primary key (id_parking)
    );
    
    create table Vol (
         id_vol numeric(100) not null,
         Heure_decollage varchar(10) not null,
         Heure_atterissage varchar(10) not null,
         constraint ID_Vol_ID primary key (id_vol)
    );

    create table Facture (
         id_facture numeric(100) not null,
         Recette_jour numeric(100) not null,
         Recette_mois numeric(100) not null,
         Recette_annee numeric(100) not null,
         Prix_Total numeric(100) not null,
         id_agent numeric(100) not null,
         constraint ID_Facture_ID primary key (id_facture),
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
         constraint ID_Reservation_ID primary key (id_reservation),
         foreign key (id_vol) references Vol(id_vol),
         foreign key (id_avion) references Avion(id_avion),
         foreign key (id_parking) references Parking(id_parking),
         foreign key (id_facture) references Facture(id_facture)
    );

    create table Emplacement (
         num_emplacement numeric(100) not null,
         id_reservation numeric(100) not null,
         id_hangar numeric(100) not null,
         constraint ID_Emplacement_ID primary key (num_emplacement),
         constraint FKLouer_ID unique (id_reservation),
         foreign key (id_hangar) references Hangar(id_hangar),
         foreign key (id_reservation) references Reservation(id_reservation)
    );

    create table Message (
         id_agent numeric(100) not null,
         id_pilote numeric(100) not null,
         Texte varchar(255) not null,
         constraint ID_Message_ID primary key (id_agent, id_pilote),
         foreign key (id_pilote) references Pilote(id_pilote),
         foreign key (id_agent) references AgentExploitation(id_agent)
    );

    create table Remplir (
         id_reservation numeric(100) not null,
         Quantite numeric(10) not null,
         Type_carburant varchar(30) not null,
         constraint FKRem_Res_ID primary key (id_reservation),
         foreign key (id_reservation) references Reservation(id_reservation),
         foreign key (Type_carburant) references Carburant(Type_carburant)
    );

    -- Index Section
    -- _____________ 

    create unique index ID_AgentExploitation_IND on AgentExploitation (id_agent);
    create index FKAuthentifier_Agent_IND on AgentExploitation (identifiant);
    create unique index ID_Avion_IND on Avion (id_avion);
    create index FKPosseder_IND on Avion (id_pilote);
    create unique index ID_Carburant_IND on Carburant (Type_carburant);
    create unique index ID_Compte_IND on Compte (identifiant);
    create unique index ID_Emplacement_IND on Emplacement (num_emplacement);
    create index FKSituer_IND on Emplacement (id_hangar);
    create unique index FKLouer_IND on Emplacement (id_reservation);
    create unique index ID_Facture_IND on Facture (id_facture);
    create index FKCreer_IND on Facture (id_agent);
    create unique index ID_Gestionnaire_Aerodrome_IND on Gestionnaire_Aerodrome (id_gestionnaire);
    create index FKAuthentifier_Gestionnaire_IND on Gestionnaire_Aerodrome (identifiant);
    create unique index ID_Hangar_IND on Hangar (id_hangar);
    create unique index ID_Message_IND on Message (id_agent, id_pilote);
    create index FKMes_Pil_IND on Message (id_pilote);
    create unique index ID_Parking_IND on Parking (id_parking);
    create unique index ID_Pilote_IND on Pilote (id_pilote);
    create index FKAuthentifier_Pilote_IND on Pilote (identifiant);
    create unique index FKRem_Res_IND on Remplir (id_reservation);
    create index FKRem_Car_IND on Remplir (Type_carburant);
    create unique index ID_Reservation_IND on Reservation (id_reservation);
    create index FKReserver_IND on Reservation (id_vol);
    create index FKConcerner_IND on Reservation (id_avion);
    create index FKAllouer_IND on Reservation (id_parking);
    create index FKAjouter_IND on Reservation (id_facture);
    create unique index ID_Vol_IND on Vol (id_vol);
""")

con.commit()
con.close()