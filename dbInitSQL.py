import os

import dbOperator
import settings
import sqlite3

conn = sqlite3.connect("testDB.db")

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
    required_minimum INTEGER
);

CREATE TABLE component_replacement (
    id INTEGER PRIMARY KEY,
    printer_number INTEGER,
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
        conn = sqlite3.connect("testDB.db")
        cursor = conn.cursor()
        sql = f"""INSERT INTO {dbOperator.WarehouseElemNote.note_type}  
        (name, current_count, required_minimum) VALUES (?, ?, ?);"""
        cursor.executemany(sql, param_list)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

create_warehouseElem()