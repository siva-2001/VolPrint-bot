API_TOKEN = '5540793759:AAF63waJNnX6k9fVQFrbNe2xDbgaMTOU6_w'


printer_count = 60
dbName = 'dataBase.db'

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


start_menu_commands = (
    'Заменить комплектующую',
    'Обновить содержимое склада',
    # 'Покупки'
    'Посмотреть историю принтера',
    'Посмотреть историю замен запчастей',
)

warehouse_update_types = (
    "Провести инвентаризацию",
    "Обновление по одной позиции"
)

warehouse_list = (
    "Коробки",
    "Клей",
    "Сопло(Н)",
    "Сопло(В)",
    "Вода",
    "Шестерня(Н)",
    "Шестерня(В)",
    "Скотч",
    "Стрэтч"
)


component_list = (
    'Сопло(В)', 'Сопло(Н)',
    'Шестерня(В)', 'Шестерня(Н)',
    'Чистка сопла',
    'ТО', 'PEI-пластина', "Тефлоновая трубка"
)
