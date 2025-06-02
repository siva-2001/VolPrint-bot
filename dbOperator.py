import datetime
import sqlite3
import re
from typing import reveal_type

import exceptions
import settings

notes = {}

#     ОБРАБОТКА ОШИБОК: ДОПИСАТЬ
def stringToDatetime(s):
    dtList = [int(s[1:]) if s[0]=="0" else int(s) for s in re.split(r'[:. ]+', s)]
    return datetime.datetime(
        year=dtList[0]+2000,
        month=dtList[1],
        day=dtList[2],
        hour=dtList[3],
        minute=dtList[4],
    )

class DBOperator():

    @staticmethod
    def writeComponentReplacement(param_list):
        try:
            conn = sqlite3.connect(settings.dbPath)
            cursor = conn.cursor()
            sql = f"INSERT INTO {ReplacementNote.note_type} (printer_number, operation, warehouseElement_name, employee_username, dateTime) VALUES (?, ?, ?, ?, ?);"

            cursor.executemany(sql, param_list)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def deleteLastComponentReplacement(printer_number):
        with sqlite3.connect(settings.dbPath) as conn:
            deleteReplNote = conn.cursor().execute(f"""
                    SELECT id, dateTime FROM component_replacement 
                    WHERE printer_number = {printer_number}
                    ORDER BY component_replacement.dateTime DESC
                    LIMIT 1;
                """).fetchall()[0]
            if stringToDatetime(deleteReplNote[1]).date() == datetime.datetime.now().date():
                conn.cursor().execute(f"DELETE FROM component_replacement WHERE id = {deleteReplNote[0]}")
                return True
            else: return False

    @staticmethod
    def editWarehouseElement(update_param_list, insert_param_list):
        try:
            conn = sqlite3.connect(settings.dbPath)
            cursor = conn.cursor()
            sql_update = f"""
                UPDATE {WarehouseElemNote.note_type}
                SET current_count = ?
                WHERE name = ?; 
            """
            sql_insert = "INSERT INTO warehouse_elem_update (warehouseElement_name, employee_username, dateTime) VALUES (?, ?, ?);"
            # добавить в warehouse_elem_update старое и новое значение позиции
            cursor.executemany(sql_update, update_param_list)
            cursor.executemany(sql_insert, insert_param_list)

            conn.commit()
        except Exception: print("EXEP")

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def getPrinterStory(number, len=999):
        if (number < 1 or number > settings.printer_count): raise exceptions.PrinterCountException

        with sqlite3.connect(settings.dbPath) as conn:

            res = conn.cursor().execute(f"""
                SELECT component_replacement.operation, component_replacement.warehouseElement_name, 
                employee.name, component_replacement.dateTime
                FROM component_replacement
                LEFT JOIN employee ON component_replacement.employee_username = employee.username
                WHERE printer_number = {number}
                ORDER BY component_replacement.dateTime DESC
                LIMIT {len};
            """).fetchall()
            res = [(" ".join(x[0:2]), x[2], stringToDatetime(x[3])) if x[1] else (x[0], x[2], stringToDatetime(x[3])) for x in res]
            return {
                "field_names" : (
                    "Операция" + 3*" ",
                    "Сотрудник" + 2*" ",
                    "Дата" + 13*" "),
                "res": res
            }

    @staticmethod
    def getWarehouseContents():
        with (sqlite3.connect(settings.dbPath) as conn):
            # format = {
            #     "field_names":["field_name1", "field_name2"],
            #     "res": [(count1, required_count1), (count2, required_count2)]
            # }
            #       добавить поля   isComponent, IOSequence

            res = conn.cursor().execute(f"""
                SELECT name, current_count, required_minimum FROM warehouse_position
                ORDER BY IOSequence;
            """).fetchall()
            return {
                "field_names": [item[0] for item in res],
                "res": [(x[1], x[2]) for x in res]
            }

    @staticmethod
    def getWarehouseList():
        with (sqlite3.connect(settings.dbPath) as conn):
            res = conn.cursor().execute(f"""
                SELECT name, current_count, required_minimum FROM warehouse_position
                ORDER BY IOSequence;
            """).fetchall()
            ans = dict()
            for elem in res: ans[elem[0]] = (elem[1], elem[2])
            return ans

    @staticmethod
    def getComponentList():
        with (sqlite3.connect(settings.dbPath) as conn):
            res = conn.cursor().execute(f"""
                SELECT name FROM warehouse_position
                WHERE isComponent = 1
                ORDER BY IOSequence;
            """).fetchall()
            return [x[0] for x in res]

    @staticmethod
    def getInventoryNeedsPositions():
        with sqlite3.connect(settings.dbPath) as conn:
            completed = conn.cursor().execute("""
                SELECT warehouseElement_name, dateTime FROM warehouse_elem_update
            """).fetchall()
            completed = [{
                "pos":el[0],
                "dateTime":stringToDatetime(el[1])
            } if stringToDatetime(el[1]).day == datetime.datetime.now().day else None for el in completed]
            completed = list(set([x["pos"] for x in completed if x]))
            res = list(DBOperator.getWarehouseList().keys())
            for el in completed: res.remove(el)
            return res

    @staticmethod
    def getResponsiblePosiotion():
        with sqlite3.connect(settings.dbPath) as conn:
            res = conn.cursor().execute("""
                SELECT employee.tg_user_id, warehouse_position.name FROM warehouse_position
                LEFT JOIN employee ON employee.username = warehouse_position.responsible_for_the_order
                WHERE current_count <=required_minimum;
            """).fetchall()
            ans = dict()
            for item in res:
                if int(item[0]) not in ans.keys(): ans[int(item[0])] = [item[1]]
                else: ans[int(item[0])].append(item[1])
            return ans

    @staticmethod
    def get_TechServices(timedelta=datetime.timedelta(days=7)):
        with sqlite3.connect(settings.dbPath) as conn:
            print("here")
            result = []
            res = conn.cursor().execute(f"""
                SELECT component_replacement.operation, employee.name, component_replacement.dateTime, component_replacement.printer_number
                FROM component_replacement
                LEFT JOIN employee ON component_replacement.employee_username = employee.username
                WHERE component_replacement.operation = "Плановое ТО"
                ORDER BY component_replacement.dateTime DESC
            """).fetchall()
            for x in res:
                if (stringToDatetime(x[2]) > datetime.datetime.now() - timedelta):
                    result.append((x[1], stringToDatetime(x[2]), x[3]))
        return result


    @staticmethod
    def getAdmins():
        with sqlite3.connect(settings.dbPath) as conn:
            return conn.cursor().execute("""
                SELECT tg_user_id, username FROM employee WHERE isAdmin = TRUE;
            """).fetchall()

class ReplacementNote():
    note_type = 'component_replacement'
    @staticmethod
    def get_component_replacement_note(user_username, text):
        if int(text) > 0 and int(text) <= settings.printer_count:
            return {
                "note_type" : ReplacementNote.note_type,
                "employee_username": user_username,
                "printer_number":int(text),
                "operation":None,
                "component": None,
                "dateTime" : datetime.datetime.now().strftime(settings.dbDatetimeFormat)
            }
        else: raise exceptions.PrinterCountException

    @staticmethod
    def writeInDB(note):
        if note["note_type"] == ReplacementNote.note_type:
            param_list = [(note["printer_number"], note["operation"], note["component"], note["employee_username"], note["dateTime"])]
            dbOperator = DBOperator()
            dbOperator.writeComponentReplacement(param_list)
            del(dbOperator)

class WarehouseElemNote():
    note_type = "warehouse_position"
    @staticmethod
    def create_warehouse_elem_note(employee_username, elem_type):
        return {
            "note_type" : WarehouseElemNote.note_type,
            "employee_username": employee_username,
            "name": elem_type,
            "count": None
        }

    @staticmethod
    def writeInDB(note):
        if note["note_type"] == WarehouseElemNote.note_type:
            update_param_list = [(note["count"], note["name"])]
            insert_param_list = [
            (note["name"], note["employee_username"], datetime.datetime.now().strftime(settings.dbDatetimeFormat))]
            dbOperator = DBOperator()
            dbOperator.editWarehouseElement(update_param_list, insert_param_list)
            del (dbOperator)

class InventoryNote():
    note_type = "inventory_note"
    @staticmethod
    def create_inventory_note():
        return {
            "note_type" : InventoryNote.note_type,
            "whElemNotes": [],
            "posList" : DBOperator.getInventoryNeedsPositions()
        }
