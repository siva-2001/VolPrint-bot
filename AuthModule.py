import settings
import sqlite3

class UserAuth():
    @staticmethod
    def userIsAuth(userID):
        try:
            conn = sqlite3.connect(settings.dbPath)
            cursor = conn.cursor()
            sql = f"SELECT name FROM employee WHERE tg_user_id = {userID};"
            res = cursor.execute(sql).fetchall()
            print(len(res))
            if len(res) == 1: return True
            elif len(res)  == 0: return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def createUser(userID, username, name):
        try:
            conn = sqlite3.connect(settings.dbPath)
            cursor = conn.cursor()
            sql = f"INSERT INTO employee (tg_user_id, username, name) VALUES (?,?,?);"
            cursor.executemany(sql, [(userID, username, name),])
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def makeUserAdmin(): pass

    @staticmethod
    def makeUserHolder(): pass
