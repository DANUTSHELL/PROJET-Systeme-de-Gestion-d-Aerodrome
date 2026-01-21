import sqlite3

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

class RequetesSQL :
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

    def CloseDB(self):
        self.con.close()
