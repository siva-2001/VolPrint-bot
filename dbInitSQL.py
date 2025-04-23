import os
import dbOperator
import settings
import sqlite3

def dbInitial():
    if not os.path.exists(settings.dbName):

        conn = sqlite3.connect(settings.dbName)

        dbInitSQL = """
        
        CREATE TABLE employee (
            tg_user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            name TEXT, 
            isAdmin INTEGER DEFAULT 0,
            isHolder INTEGER DEFAULT 0
        );
        
        CREATE TABLE warehouse_position (
            name TEXT PRIMARY KEY,
            current_count INTEGER,
            required_minimum INTEGER,
            responsible_for_the_order TEXT NOT NULL,
            FOREIGN KEY (responsible_for_the_order) REFERENCES employee (tg_user_id)
        );
        
        CREATE TABLE component_replacement (
            id INTEGER PRIMARY KEY,
            printer_number INTEGER,
            operation TEXT,
            warehouseElement_name TEXT,
            employee_id INTEGER,
            dateTime TEXT,
            FOREIGN KEY (warehouseElement_name)  REFERENCES warehouse_position (name),
            FOREIGN KEY (employee_id)  REFERENCES employee (tg_user_id)
        );
        
        CREATE TABLE warehouse_elem_update (
            id INTEGER PRIMARY KEY,
            warehouseElement_name TEXT,
            employee_id INTEGER,
            dateTime TEXT,
            FOREIGN KEY (employee_id)  REFERENCES employee (tg_chat_id),
            FOREIGN KEY (warehouseElement_name)  REFERENCES warehouse_position (name)
        );
        """

        conn.executescript(dbInitSQL)
        conn.commit()
        conn.close()


        def create_warehouseElem():
            param_list = [(e, 0, 0) for e in settings.warehouse_list]
            try:
                conn = sqlite3.connect(settings.dbName)
                cursor = conn.cursor()
                cursor.executescript(f"""INSERT INTO employee  
                    (username, tg_user_id, name) VALUES ("siva", "808976737", "siva");""")
                sql = f"""INSERT INTO {dbOperator.WarehouseElemNote.note_type}  
                    (name, current_count, required_minimum, responsible_for_the_order) VALUES (?, ?, ?, "808976737");"""
                cursor.executemany(sql, param_list)
                conn.commit()
            finally:
                cursor.close()
                conn.close()

        create_warehouseElem()
        print(f"База данных создана: {settings.dbName}")
    else:
        print(f"База данных существует: {settings.dbName}")