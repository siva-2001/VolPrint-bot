import os

import dbOperator
import settings
import sqlite3

conn = sqlite3.connect("testDB.db")


dbInitSQL = f"""

CREATE TABLE employee (
    tg_chat_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    name TEXT, 
    isAdmin INTEGER DEFAULT 0,
    isHolder INTEGER DEFAULT 0
);

CREATE TABLE {dbOperator.WarehouseElemNote.note_type} (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    current_count INTEGER,
    required_minimum INTEGER
);

CREATE TABLE {dbOperator.ReplacementNote.note_type} (
    id PRIMARY KEY,
    printer_number INTEGER,
    warehouseElementID INTEGER,
    employee INTEGER,
    FOREIGN KEY (warehouseElementID)  REFERENCES {dbOperator.WarehouseElemNote.note_type} (id)
);

CREATE TABLE warehouse_elem_update (
    id PRIMARY KEY,
    warehouseElementID INTEGER,
    employee INTEGER,
    dateTime TEXT,
    FOREIGN KEY (employee)  REFERENCES employee (tg_chat_id),
    FOREIGN KEY (warehouseElementID)  REFERENCES {dbOperator.WarehouseElemNote.note_type} (id)
);
"""

conn.executescript(dbInitSQL)