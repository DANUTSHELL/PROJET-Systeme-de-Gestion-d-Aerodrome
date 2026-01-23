import sqlite3

#   Fonctions pour parcourir les listes et les transformer en des phrases
def parcours_listes(L1,L2):
    attributs = ""
    taille = len(L1)

    for i in range(taille):
        attributs = attributs + f"{L1[i]} {L2[i]}"

        if i< taille - 1:
            attributs = attributs + ", "
    return attributs

def parcours_valeurs_interrogation(L):
    nouveau = ""
    taille = len(L)

    for i in range(taille):
        nouveau = nouveau + f"?"

        if i< taille - 1:
            nouveau = nouveau + ", "
    return nouveau

#   Class RequeteSQL qui regroupe toutes les requêtes SQL

class RequeteSQL :
    def __init__(self, baseDB):
        self.con = sqlite3.connect(baseDB)
        self.cur = self.con.cursor()

    def CreateTable(self, nomTable, listeAttributs, typeAttributs, PrimaryKey):
        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {nomTable}(
                         {parcours_listes(listeAttributs, typeAttributs)},PRIMARY KEY ({PrimaryKey})
                         )""")
        self.con.commit()
    
    def Insert(self, nomTable, listeValeurs):
        self.cur.execute(f"""INSERT INTO {nomTable} VALUES(
                         {parcours_valeurs_interrogation(listeValeurs)}
                         )""", listeValeurs)
        self.con.commit()

    def Update(self, nomTable, nouvelle_valeur, conditions):
        self.cur.execute(f"""UPDATE {nomTable} SET {nouvelle_valeur} WHERE {conditions}
                         """)
        self.con.commit()
    
    def Delete(self, nomTable, conditions):
        self.cur.execute(f"""DELETE FROM {nomTable} WHERE {conditions}
                         """)
        self.con.commit()

    def Select(self, colonnes, nomTable, conditions):
        self.cur.execute(f"""SELECT {colonnes} FROM {nomTable} WHERE {conditions}
                         """)
        resultats = self.cur.fetchall()
        return resultats

    def CloseDB(self):
        self.con.close()
