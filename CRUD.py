import sqlite3

#   Class RequeteSQL qui regroupe toutes les requêtes SQL

class RequeteSQL :
    def __init__(self, baseDB):
        self.con = sqlite3.connect(baseDB)
        self.cur = self.con.cursor()

    def CreateTable(self, nomTable, listeAttributs, typeAttributs, PrimaryKey):
        attributs_str = ", ".join([f"{attributs} {types}" for attributs, types in zip(listeAttributs, typeAttributs)])
        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS {nomTable}(
                         {attributs_str},PRIMARY KEY ({PrimaryKey})
                         )""")
        self.con.commit()
    
    def Insert(self, nomTable, listeValeurs):
        Liste_interrogations = ", ".join(["?" for _ in listeValeurs])
        self.cur.execute(f"""INSERT INTO {nomTable} VALUES(
                         {Liste_interrogations}
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

    def Select(self, colonnes, nomTable, conditions = None):
        if conditions is None:
            self.cur.execute(f"""SELECT * FROM {nomTable}""")
        else:
            self.cur.execute(f"""SELECT {colonnes} FROM {nomTable} WHERE {conditions}
                             """)
        resultats = self.cur.fetchall()
        return resultats

    def CloseDB(self):
        self.con.close()
