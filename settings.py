API_TOKEN = "5540793759:AAFcStMnOLcuth1CntvQHF6ptu-Ilev7G24"

printer_count = 60
dbName = 'testDB.db'

hello_question = "Привет! Чем займёмся?"
printer_number_request = "Введи номер принтера"
int_value_error_message = "Нужно ввести целое число"
component_request = "Что меняем / устанавливаем?"
warehouse_element_type_request = "Количество чего обновим?"
warehouse_elem_undef = "На складе нет такой позиции!"
inventory_end_message = "Инвентаризация завершена"
success_msg = "Готово"

def warehouse_elem_count_request(elem):
    return f"Введите количество позиции [{elem}]:" if isinstance(elem, str) else None


start_menu_commands = {
    'comp_replacement' : 'Заменить комплектующую',
    'warehouse_update' : 'Обновить содержимое склада',
    'printer_story' : 'Посмотреть историю принтера',
    'warehouse' : 'Содержимое склада'
    # 'Посмотреть историю замен запчастей',
}

warehouse_update_types = (
    "Провести инвентаризацию",
    "Обновление по одной позиции"
)

component_list = (
    'Сопло(В)',
    'Сопло(Н)',
    'Шестерня(В)',
    'Шестерня(Н)',
    'PEI-пластина',
    "Тефлоновая трубка",
    "Кулер",
    "Кулер-улитка",
    'ТО',                       # НЕ ЭЛЕМЕНТЫ
    'Чистка сопла',
)

warehouse_list = tuple(list(component_list) + [
    "Коробки",
    "Клей",
    "Вода",
    "Скотч",
    "Стрэтч",
    "Зип-пактеы",
    "Мусорные пакеты",
    "Пена",
    "Спирт",
    "Тканевая салфетка",
    "Смазка"
])