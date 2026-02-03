import sqlite3

class RequeteSQL:
    def __init__(self, baseDB):
        self.con = sqlite3.connect(baseDB, check_same_thread=False)
        self.cur = self.con.cursor()

    def CreateTable(self, nomTable, listeAttributs, typeAttributs, PrimaryKey):
        attributs_str = ", ".join([f"{att} {typ}" for att, typ in zip(listeAttributs, typeAttributs)])
        query = f"CREATE TABLE IF NOT EXISTS {nomTable} ({attributs_str}, PRIMARY KEY ({PrimaryKey}))"
        self.cur.execute(query)
        self.con.commit()
    
    def Insert(self, nomTable, listeValeurs):
        placeholders = ", ".join(["?" for _ in listeValeurs])
        query = f"INSERT INTO {nomTable} VALUES ({placeholders})"
        self.cur.execute(query, listeValeurs)
        self.con.commit()

    def Update(self, nomTable, colonne, valeur, condition):
        query = f"UPDATE {nomTable} SET {colonne} = ? WHERE {condition}"
        self.cur.execute(query, (valeur,))
        self.con.commit()
    
    def Delete(self, nomTable, colonne_cond, valeur_cond):
        query = f"DELETE FROM {nomTable} WHERE {colonne_cond} = ?"
        self.cur.execute(query, (valeur_cond,))
        self.con.commit()

    def Select(self, nomTable, conditions=None):
        if conditions is None:
            query = f"SELECT * FROM {nomTable}"
        else:
            query = f"SELECT * FROM {nomTable} WHERE {conditions}"
            
        self.cur.execute(query)
        return self.cur.fetchall()

    def CloseDB(self):
        self.con.close()