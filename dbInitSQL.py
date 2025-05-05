import os
import dbOperator
import settings
import sqlite3
import  re

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
    responsible_for_the_order TEXT,
    isComponent INTEGER DEFAULT 0,
    IOSequence INTEGER DEFAULT 0,
    FOREIGN KEY (responsible_for_the_order) REFERENCES employee (username)
);

CREATE TABLE component_replacement (
    id INTEGER PRIMARY KEY,
    printer_number INTEGER,
    operation TEXT,
    warehouseElement_name TEXT,
    employee_username INTEGER,
    dateTime TEXT,
    FOREIGN KEY (warehouseElement_name)  REFERENCES warehouse_position (name),
    FOREIGN KEY (employee_username)  REFERENCES employee (username)
);

CREATE TABLE warehouse_elem_update (
    id INTEGER PRIMARY KEY,
    warehouseElement_name TEXT,
    employee_username INTEGER,
    dateTime TEXT,
    FOREIGN KEY (employee_username)  REFERENCES employee (username),
    FOREIGN KEY (warehouseElement_name)  REFERENCES warehouse_position (name)
);
"""

def dbInitial():
    if not os.path.exists(settings.dbPath):
        conn = sqlite3.connect(settings.dbPath)
        conn.executescript(dbInitSQL)
        conn.commit()
        conn.close()

        print(f"База данных создана: {settings.dbPath}")
    else:
        print(f"База данных существует: {settings.dbPath}")

def uploadPrinterHistory(fileName):
    file = open(fileName, "r")
    for ind, line in enumerate(file):
        lineEl = re.split(r'[_\n]', line)
        print(lineEl)
        printerNumber = int(lineEl[0]) if (int(lineEl[0]) > 0 and int(lineEl[0]) < settings.printer_count) else None
        if (lineEl[1][:6] == "Замена"):
            if len(lineEl[1]) > 6: print(f"Ошибка при считывании файла. Строка {ind+1}: {line}")
            elif lineEl[2] in settings.component_list: operation, component, dtStr = lineEl[1], lineEl[2], lineEl[3]
            else: print(f"Ошибка при считывании файла. Строка {ind+1}: {line}")
        elif lineEl[1] in settings.event_list: operation, component, dtStr = lineEl[1], None, lineEl[2]
        dt = dbOperator.stringToDatetime(dtStr)


        print(printerNumber, operation, component, dt)


