# Système de Gestion d'Aérodrome

Ce projet est un système de gestion complet pour un aérodrome privé, conçu pour gérer les opérations, les réservations, la facturation et le personnel.

## 🌟 Fonctionnalités

Le système offre une gamme complète de fonctionnalités pour la gestion d'un aérodrome :

- **Gestion des utilisateurs :** Prise en charge de différents rôles avec des permissions distinctes (Gestionnaire, Agent d'exploitation, Pilote).
- **Gestion des aéronefs :** Suivi des avions, de leurs types, de leur capacité en carburant et de leurs pilotes attitrés.
- **Gestion des infrastructures :** Administration des hangars et des places de parking, y compris leur disponibilité et leur tarification.
- **Système de vols et de réservations :** Enregistrement des informations de vol et gestion complète des réservations, liant vols, aéronefs, et services.
- **Gestion des ressources :** Suivi des stocks de carburant (différents types, prix, quantités) et gestion des opérations de ravitaillement.
- **Facturation :** Génération et suivi des factures pour l'ensemble des services fournis.
- **Communication interne :** Système de messagerie pour faciliter la communication entre les agents d'exploitation et les pilotes.

## 🛠️ Technologies utilisées

- **Langage :** Python 3
- **Framework Web :** FastAPI
- **Base de données :** SQLite
- **Serveur d'application :** Uvicorn (pour l'exécution de FastAPI)

## 🗂️ Structure de la base de données

La base de données `Aerodrome.db` est le cœur du système. Elle est composée des tables principales suivantes :

- `Compte` : Gère les identifiants de connexion pour tous les utilisateurs.
- `Pilote`, `AgentExploitation`, `Gestionnaire_Aerodrome` : Définissent les rôles et les informations spécifiques à chaque type d'utilisateur.
- `Avion` : Contient les informations sur les aéronefs.
- `Hangar`, `Parking` : Gèrent les infrastructures de stationnement.
- `Vol`, `Reservation` : Assurent le suivi des vols et des réservations associées.
- `Carburant`, `Remplir` : Gèrent les stocks et les opérations de ravitaillement.
- `Facture` : Stocke toutes les informations de facturation.

Un diagramme de la base de données est disponible dans le dossier `Diagrammes/`.

## 🚀 Installation et Lancement

Suivez ces étapes pour mettre en place et lancer le projet sur votre machine locale.

### 1. Prérequis

Assurez-vous d'avoir Python 3.8+ installé sur votre système.

### 2. Installation

Clonez ce dépôt et installez les dépendances nécessaires :

```bash
git clone https://VOTRE_URL_DE_CLONAGE/PROJET-Systeme-de-Gestion-d-Aerodrome.git
cd PROJET-Systeme-de-Gestion-d-Aerodrome
pip install fastapi "uvicorn[standard]"
```

### 3. Création de la base de données

Exécutez le script `DB_Creation.py` pour créer la structure de la base de données :

```bash
python DB_Creation.py
```

### 4. Peuplement de la base de données (Optionnel)

Pour remplir la base de données avec un jeu de données de test complet, exécutez le script `Test.py` :

```bash
python Test.py
```
Cela créera de nombreux pilotes, avions, réservations, etc., pour vous permettre de tester l'application dans des conditions réalistes.

### 5. Lancement du serveur

Lancez l'application web avec Uvicorn :

```bash
uvicorn Main:app --reload
```

Le serveur sera accessible à l'adresse `http://127.0.0.1:8000`.

## 📂 Structure du projet

```
.
├── Aerodrome.db          # La base de données SQLite
├── CRUD.py               # Contient la logique d'accès aux données (Create, Read, Update, Delete)
├── DB_Creation.py        # Script pour initialiser le schéma de la base de données
├── Main.py               # Point d'entrée de l'application web FastAPI
├── README.md             # Ce fichier
├── Test.py               # Script pour peupler la base de données avec des données de test
└── Diagrammes/
    ├── ...               # Fichiers de conception et diagrammes de la base de données
```