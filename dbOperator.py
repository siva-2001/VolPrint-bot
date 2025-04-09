import sqlite3


notes = {}
conn = sqlite3.connect('dataBase.db')

class ReplacementNote():
    @staticmethod
    def create_component_replacement_note(message):
        notes[message.from_user.id] = {
            "note_type" : "component_replacement",
            "username": message.from_user.username,
            "printer_number":int(message.text),
            "component":None
        }


class WarehouseElemNote():
    @staticmethod
    def create_warehouse_elem_note(message):
        notes[message.from_user.id] = {
            "note_type" : "warehouse_elem",
            "username": message.from_user.username,
            "element_type": message.text,
            "count": None
        }

def create_inventory_note(message):
    notes[message.from_user.id] = {
        "note_type" : "inventory_note",
        "username": message.from_user.username,

    }