printer_count = 60
main_chat_id = 808976737
dbName = 'testDB.db'
dbDatetimeFormat = "%y.%m.%d %H:%M"

hello_question = "Привет! Чем займёмся?"
printer_number_request = "Введи номер принтера"
int_value_error_message = "Нужно ввести целое число"
event_request = "Что будем делать?"
warehouse_element_type_request = "Количество чего обновим?"
warehouse_elem_undef = "На складе нет такой позиции!"
inventory_end_message = "Инвентаризация завершена"
success_msg = "Готово"
undef_event_message = "Неизвестная операция"

def warehouse_elem_count_request(elem):
    return f"Введите количество позиции [{elem}]:" if isinstance(elem, str) else None


start_menu_commands = {
    'comp_replacement' : 'Обслужим принтер',
    'warehouse_update' : 'Обновить содержимое склада',
    'printer_story' : 'Посмотреть историю принтера',
    'warehouse' : 'Содержимое склада',
    # 'Посмотреть историю замен запчастей',
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