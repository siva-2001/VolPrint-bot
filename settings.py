"""
В среде окружения необходимы переменные:
API_TOKEN - телеграм API токен
REG_PW - Регистрационный пароль
"""
import os, sys

printer_count = 60
main_chat_id = 808976737
adminID = 808976737

API_TOKEN = os.environ.get("API_TOKEN")
REG_PW = os.environ.get("REG_PW")


dbName = "DB.db"
dbPath = 'data/test.db' if os.environ.get("IS_DEVELOPMENT_ENV") else '/data/'+dbName

dbDatetimeFormat = "%y.%m.%d %H:%M"

int_value_error_message = "Нужно ввести целое положительное число"

def warehouse_elem_count_request(elem):
    return f"Введите количество позиции [{elem}]:" if isinstance(elem, str) else None


start_menu_commands = {
    'comp_replacement' : 'Обслужим принтер',
    'warehouse_update' : 'Обновить содержимое склада',
    'printer_story' : 'Посмотреть историю принтера',
    'warehouse' : 'Содержимое склада',
}

warehouse_update_types = (
    "Провести инвентаризацию",
    "Обновление по одной позиции",
)

component_list = (
    'Сопло(В)',
    'Сопло(Н)',
    'Шестерня(В)',
    'Шестерня(Н)',
    'PEI-пластина',
    "Тефлон",
    "Кулер барьера",
    "Кулер-улитка",
    "Плата головы",
)

event_list = (
    'Замена',
    'Плановое ТО',
    'Чистка сопла',
    'Чистка шестерни',
)

warehouse_list = tuple(set(list(component_list) + [
    "Коробки",
    "Клей",
    "Вода",
    "Скотч",
    "Стрэтч",
    "Зип-пакеты",
    "Мусор. пакеты",
    "Пена",
    "Спирт",
    "Ткан. салфетка",
    "Смазка"
]))
