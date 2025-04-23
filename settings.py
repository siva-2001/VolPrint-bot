import os

printer_count = 60
main_chat_id = 808976737
dbName = 'testDB.db'

API_TOKEN = os.environ.get("API_TOKEN")

if not API_TOKEN: print("API-токен отсутствует в среде окружения")

dbDatetimeFormat = "%y.%m.%d %H:%M"

int_value_error_message = "Нужно ввести целое число"

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
)

event_list = (
    'Замена компл.',
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