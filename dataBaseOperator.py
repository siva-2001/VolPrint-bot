import sqlite3



class DBOperator():
    conn = sqlite3.connect('dataBase.db')

    def addComponentReplaceNote(self, note):
        print(note)
        pass

    def updateWarehouseElement(self, note):
        print(note)
        pass

    def inventory_end(self): pass

