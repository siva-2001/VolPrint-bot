"""
В среде окружения необходимы переменные:
API_TOKEN - телеграм API токен
REG_PW - Регистрационный пароль
"""
import os, sys


printer_count = 60 if not os.environ.get("PRINTER_COUNT") else int(os.environ.get("PRINTER_COUNT"))
main_chat_id = os.environ.get("MAIN_CHAT_ID")
API_TOKEN = os.environ.get("API_TOKEN")
REG_PW = os.environ.get("REG_PW")
DBName = "test.db" if not os.environ.get("DB_NAME") else os.environ.get("DB_NAME")
dbPath = 'data/' + DBName if os.environ.get("IS_DEVELOPMENT_ENV") else '/data/' + DBName

dbDatetimeFormat = "%y.%m.%d %H:%M"

int_value_error_message = "Нужно ввести целое положительное число"

def warehouse_elem_count_request(elem):
    return f'Введите количество позиции "{elem}":' if isinstance(elem, str) else None


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

event_list = (
    # В ДАННОМ СПИСКЕ "ЗАМЕНА" ДОЛЖНА БЫТЬ ПЕРВОЙ
    'Замена',
    'Плановое ТО',
    'Чистка сопла',
    'Чистка шестерни',
    'Обрезка тефлона'
)
