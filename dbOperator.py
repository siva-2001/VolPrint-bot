import datetime
import sqlite3
import re
from typing import reveal_type

import settings

notes = {}


#     ОБРАБОТКА ОШИБОК: ДОПИСАТЬ
def stringToDatetime(s):

    def datetimeList(s):
        if len(s) == 14:
            return [int(s[1:]) if s[0]=="0" else int(s) for s in re.split(r'[:. ]+', s)]
        else: return  "Неверный формат времени"

    dtList = datetimeList(s)
    dt = datetime.datetime(
        year=dtList[4]+2000,
        month=dtList[3],
        day=dtList[2],
        hour=dtList[0],
        minute=dtList[1],
    )
    print(dt, type(dt))
    return dt



class DBOperator():

    @staticmethod
    def writeComponentReplacement(param_list):
        try:
            conn = sqlite3.connect(settings.dbName)
            cursor = conn.cursor()
            sql = f"INSERT INTO {ReplacementNote.note_type} (printer_number, warehouseElement_name, employee_id, dateTime) VALUES (?, ?, ?, ?);"

            cursor.executemany(sql, param_list)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def editWarehouseElement(update_param_list, insert_param_list):
        try:
            conn = sqlite3.connect(settings.dbName)
            cursor = conn.cursor()
            sql_update = f"""
                UPDATE {WarehouseElemNote.note_type}
                SET current_count = ?
                WHERE name = ?; 
            """
            sql_insert = "INSERT INTO warehouse_elem_update (warehouseElement_name, employee_id, dateTime) VALUES (?, ?, ?);"

            cursor.executemany(sql_update, update_param_list)
            cursor.executemany(sql_insert, insert_param_list)

            conn.commit()
        except Exception:
            print("EXEP")

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def getPrinterStory(number):
        with sqlite3.connect(settings.dbName) as conn:
            res = conn.cursor().execute(f"""
                SELECT component_replacement.warehouseElement_name, employee.username, component_replacement.dateTime 
                FROM component_replacement
				JOIN employee ON component_replacement.employee_id = employee.tg_user_id
                WHERE printer_number = {number};
            """).fetchall()
            print(res)

            return {
                "field_names" : (
                    "Заменено" + 5*" ",
                    "Сотрудник" + 3*" ",
                    "Дата" + 14*" "),
                "res": res
            }

    @staticmethod
    def getWarehouseContents():
        with sqlite3.connect(settings.dbName) as conn:
            res = conn.cursor().execute(f"""
                        SELECT name, current_count FROM warehouse_position;
                    """).fetchall()
            print(res)
            return res

    @staticmethod
    def getInventoryNeedsPositions():
        with sqlite3.connect(settings.dbName) as conn:
            completed = conn.cursor().execute("""
                SELECT warehouseElement_name, dateTime FROM warehouse_elem_update
            """).fetchall()
            completed = [{
                "pos":el[0],
                "dateTime":stringToDatetime(el[1])
            } if stringToDatetime(el[1]).day == datetime.datetime.now().day else None for el in completed]
            completed = [x["pos"] for x in completed if x]
            res = list(settings.component_list) + list(settings.warehouse_list)
            for el in completed: res.remove(el)
            return res

    def addUser(self): pass

    def userIsAuth(self):
        return True

class ReplacementNote():
    note_type = 'component_replacement'
    @staticmethod
    def get_component_replacement_note(message):
        return {
            "note_type" : ReplacementNote.note_type,
            "employee_id": message.from_user.id,
            "printer_number":int(message.text),
            "event":None,
            "dateTime" : datetime.datetime.now().strftime('%H:%M %d.%m.%y')
        }

    @staticmethod
    def writeInDB(message):
        if notes[message.from_user.id]["note_type"] == ReplacementNote.note_type:
            note = notes[message.from_user.id]
            param_list = [(note["printer_number"], note["event"], note["employee_id"], note["dateTime"])]
            dbOperator = DBOperator()
            dbOperator.writeComponentReplacement(param_list)
            del(dbOperator)

class WarehouseElemNote():
    note_type = "warehouse_position"
    @staticmethod
    def create_warehouse_elem_note(employee_id, elem_type):
        return {
            "note_type" : WarehouseElemNote.note_type,
            "employee_id": employee_id,
            "name": elem_type,
            "count": None
        }

    @staticmethod
    def writeInDB(message):
        if notes[message.from_user.id]["note_type"] == WarehouseElemNote.note_type:
            note = notes.pop(message.from_user.id)
            update_param_list = [(note["count"], note["name"])]
            insert_param_list = [(note["name"], note["employee_id"], datetime.datetime.now().strftime('%H:%M %d.%m.%y'))]
            dbOperator = DBOperator()
            dbOperator.editWarehouseElement(update_param_list,  insert_param_list)
            del(dbOperator)

class InventoryNote():
    note_type = "inventory_note"
    @staticmethod
    def create_inventory_note():
        return {
            "note_type" : InventoryNote.note_type,
            "whElemNotes": [],
            "posList" : DBOperator.getInventoryNeedsPositions()
        }

    @staticmethod
    def writeElemValue(user_id, username, count, elem_type):
        notes[user_id]["whElemNotes"][-1]["count"] = int(count)
        notes[user_id]["whElemNotes"].append(
            WarehouseElemNote.create_warehouse_elem_note(username, elem_type)
        )

    @staticmethod
    def end(): pass
