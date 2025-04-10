import datetime
import sqlite3
import settings

notes = {}

class DBOperator():
    def __init__(self):
        self.conn = sqlite3.connect(settings.dbName)
        self.cursor = self.conn.cursor()
    def writeComponentReplacement(self): pass
    def editWarehouseElement(self): pass





class ReplacementNote():
    note_type = 'component_replacement'
    @staticmethod
    def get_component_replacement_note(message):
        return {
            "note_type" : ReplacementNote.note_type,
            "username": message.from_user.username,
            "printer_number":int(message.text),
            "component":None
        }

class WarehouseElemNote():
    note_type = "warehouse_position"
    @staticmethod
    def create_warehouse_elem_note(username, elem_type):
        return {
            "note_type" : WarehouseElemNote.note_type,
            "username": username,
            "element_type": elem_type,
            "count": None
        }

    @staticmethod
    def writeInDB(message):
        if notes[message.from_user.id]["type"] == WarehouseElemNote.note_type:
            DBOperator.editWarehouseElement(message.from_user.id)

class InventoryNote():
    note_type = "inventory_note"
    @staticmethod
    def create_inventory_note(message):
        return {
            "note_type" : InventoryNote.note_type,
            "username": message.from_user.username,
            "dateTime": datetime.datetime.now(),                                       #   ТЕКУЩИЙ МОМЕНТ
            "whElemNotes": [],
            "posList" : list(settings.warehouse_list)
        }

    @staticmethod
    def writeElemValue(user_id, username, count, elem_type):
        notes[user_id]["whElemNotes"][-1]["count"] = int(count)
        notes[user_id]["whElemNotes"].append(
            WarehouseElemNote.create_warehouse_elem_note(username, elem_type)
        )

    @staticmethod
    def end(): pass
