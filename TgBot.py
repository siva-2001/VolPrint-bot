import datetime
import telebot
import settings, exceptions, dbOperator
import AuthModule

bot = telebot.TeleBot(settings.API_TOKEN, parse_mode="HTML", skip_pending=True)

def cancelDecorator(func):
    def wrapper(*args, **kwargs):
        if args[0].text== "Отмена":
            bot.clear_step_handler_by_chat_id(chat_id=args[0].from_user.id)
            if args[0].from_user.id in dbOperator.notes.keys(): dbOperator.notes.pop(args[0].from_user.id)
            handle_start_message(*args, **kwargs)
        else: func(*args, **kwargs)
    return wrapper

def checkAuthDecorator(func):
    def wrapper(*args, **kwargs):
        import AuthModule
        if AuthModule.UserAuth.userIsAuth(args[0].from_user.id): func(*args, **kwargs)
        else:
            reply_with_buttons(
                chat_id=args[0].from_user.id,
                text="У тебя нет прав для этого действия. Необходимо зарегистрироваться",
                buttons_list=["Ок"],
                withoutCancel=True,
            )
    return wrapper

def checkInput(func):
    def wrapper(*args, **kwargs):
        if len(args[0].text) > 4096:
            args[0].text = args[0].text[:4095]
        func(*args, **kwargs)


    return wrapper

def table_notes_msg_view(title, param_names, param_tuple_list):
    param_names = [name.join(["<b>", "</b>"]) for name in param_names]
    text = title + "\n\n"
    for note in param_tuple_list:
        note = list(note)
        for i in range(len(note)):
            if isinstance(note[i], datetime.datetime): note[i] = note[i].strftime("%H:%M %d.%m.%y")
            if note[i] is None: note[i] = "Не известно"
        param_iterator = zip(param_names, note)
        str_list = list()
        for param in param_iterator: str_list.append(" ".join(param))
        text = text + "\n".join(str_list) + "\n\n"
    return text

def list_notes_msg_view(title, param_names, param_list):
    param_names = [name.join(["<b>", "</b>"]) for name in param_names]
    text = title + "\n\n"
    for i in range(len(param_list)):
        if isinstance(param_list[i], datetime.datetime): param_list[i] = param_list[i].strftime("%H:%M %d.%m.%y")
        if param_list[i] is None: param_list[i] = "Не известно"
    str_list = list()
    for note in zip(param_names, param_list):
        str_list.append(" ".join([str(x) for x in note]))
    return text + "\n".join(str_list) + "\n\n"

def reply_with_buttons(chat_id, text, buttons_list=None, withoutCancel=False, next_step=None, row_width=1):
    btn_list = list()
    if not withoutCancel: btn_list.append("Отмена")
    if buttons_list: btn_list = list(buttons_list) + btn_list
    reply_markup = telebot.types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True, one_time_keyboard=True)
    reply_markup.add(*btn_list)
    if next_step:
        bot.register_next_step_handler(
            bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup = reply_markup,
            ),
            next_step
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        ),

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

#       СЦЕНАРИЙ РЕГИСТРАЦИИ
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

@bot.message_handler(commands=["registration"])
def user_registration(message):
    if not AuthModule.UserAuth.userIsAuth(message.from_user.id):
        reply_with_buttons(
            chat_id=message.from_user.id,
            text="Введи кодовую строку:",
            next_step=user_registration2,
        )
    else:
        reply_with_buttons(
            chat_id=message.from_user.id,
            text="Ты уже зарегистрирован!",
            buttons_list=["Ок"], withoutCancel=True,
        )

def user_registration2(message):
    if settings.REG_PW is None:
        reply_with_buttons(
            chat_id=message.from_user.id,
            text="Регистрационный пароль не задан, регистрация новых пользователей временно недоступна.",
            next_step=user_registration3,
        )
    #     РАССЫЛКА СООБЩЕНИЯ ОБ ОШИБКЕ АДМИНАМ
    else:
        if message.text == settings.REG_PW:
            reply_with_buttons(
                chat_id=message.from_user.id,
                text="Как тебя зовут?",
                next_step=user_registration3,
            )
        else:
            reply_with_buttons(
                chat_id=message.from_user.id,
                text="Кодовая строка не верная. \nПопробуй ещё раз:",
                next_step=user_registration2,
            )


def user_registration3(message):
    AuthModule.UserAuth.createUser(
        userID=message.from_user.id,
        username=message.from_user.username,
        name = message.text,
    )
    reply_with_buttons(
        chat_id=message.from_user.id,
        text="Готово",
        buttons_list=["Ок"], withoutCancel=True,
    )

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

#       СЦЕНАРИЙ ЗАМЕНЫ КОМПЛЕКТУЮЩЕЙ
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________


@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["comp_replacement"])
@checkAuthDecorator
def handle_component_replacement(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text="Введите номер принтера:",
        next_step=component_replacement_step1,
    )

@cancelDecorator
def component_replacement_step1(message):
    try:
        dbOperator.notes[message.from_user.id] = dbOperator.ReplacementNote.get_component_replacement_note(message)
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Что будем делать?",
            next_step=component_replacement_step2,
            buttons_list=settings.event_list
        )
    except ValueError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.int_value_error_message,
            next_step=component_replacement_step1,
        )
    except exceptions.PrinterCountException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Имеющееся количество принтеров:{}\nПопробуйте ещё раз",
            next_step=component_replacement_step1,
        )

@cancelDecorator
def component_replacement_step2(message):
    try:
        if not message.text in settings.event_list: raise exceptions.IventException
        dbOperator.notes[message.from_user.id]['operation'] = message.text
        if message.text == settings.event_list[0]:
            reply_with_buttons(
                chat_id=message.chat.id,
                text="Какой компонент будем менять?",
                next_step=component_replacement_step3,
                buttons_list=settings.component_list
            )
        else:
            note =  dbOperator.notes.pop(message.from_user.id)
            dbOperator.ReplacementNote.writeInDB(note)
            reply_with_buttons(
                chat_id=message.chat.id,
                text="Готово!",
                withoutCancel=True,
                buttons_list=["На главную"]
            )
    except exceptions.IventException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Неизвестная операция",
            next_step=component_replacement_step2,
            buttons_list=settings.event_list
        )

@cancelDecorator
def component_replacement_step3(message):
    try:
        if not message.text in settings.component_list: raise exceptions.ComponentException
        note = dbOperator.notes.pop(message.from_user.id)
        note['component'] = message.text
        dbOperator.ReplacementNote.writeInDB(note)
        reply_with_buttons(
            chat_id=message.chat.id,
            text=f'Готово! Проведена операция: {note["operation"]} "{note["component"]}"',
            withoutCancel=True,
            buttons_list=["Ок"]
        )
    except exceptions.ComponentException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Введено неизвестное имя компонента",
            next_step=component_replacement_step3,
            buttons_list=settings.event_list
        )

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
#       СЦЕНАРИЙ ОБНОВЛЕНИЯ СКЛАДА
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________


@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["warehouse_update"])
@checkAuthDecorator
def handle_warehouse_update(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text="Что будем делать?",
        next_step=warhouse_update_step_1,
        buttons_list=settings.warehouse_update_types
    )

@cancelDecorator
def warhouse_update_step_1(message):
    if message.text == settings.warehouse_update_types[0]: inventory_start(message)
    elif message.text == settings.warehouse_update_types[1]: warehouse_update_step_2(message)
    else:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Команда не распознана",
            next_step=handle_warehouse_update,
            buttons_list=settings.warehouse_update_types
        )

# @checkInput
@cancelDecorator
def inventory_start(message):
    try:
        dbOperator.notes[message.from_user.id] = dbOperator.InventoryNote.create_inventory_note()

        elem_type = dbOperator.notes[message.from_user.id]["posList"].pop(0)
        dbOperator.notes[message.from_user.id]["whElemNotes"].append(
            dbOperator.WarehouseElemNote.create_warehouse_elem_note(message.from_user.id, elem_type)
        )

        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.warehouse_elem_count_request(elem_type),
            next_step=inventory_circle
        )
    except IndexError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Все данные актуальны",
            buttons_list=["Ок"]
        )
        inventory_end(message)

@cancelDecorator
def inventory_circle(message):
    try:
        whEl = dbOperator.notes[message.from_user.id]["whElemNotes"].pop(0)
        whEl["count"] = int(message.text)
        dbOperator.WarehouseElemNote.writeInDB(whEl)
        elem_type = dbOperator.notes[message.from_user.id]["posList"].pop(0)
        dbOperator.notes[message.from_user.id]["whElemNotes"].append(
            dbOperator.WarehouseElemNote.create_warehouse_elem_note(message.from_user.id, elem_type)
        )
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.warehouse_elem_count_request(elem_type),
            next_step=inventory_circle,
        )


    except ValueError:
        dbOperator.notes[message.from_user.id]["whElemNotes"].append(whEl)
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.int_value_error_message,
            next_step=inventory_circle,
        )
    except IndexError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Инвентаризация завершена!",
            buttons_list=["Ок"], withoutCancel=True,
        )
        inventory_end(message)

@cancelDecorator
def inventory_end(message):
    dbOperator.notes.pop(message.from_user.id)
    responsibles = dbOperator.DBOperator.getResponsiblePosiotion()
    for id in responsibles.keys():
        text = "Чел, срочно закупись:\n\n"
        reply_with_buttons(chat_id=id, text=text+"\n".join(responsibles[id]))


@cancelDecorator
def warehouse_update_step_2(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text="Какую позицию обновим?",
        buttons_list=settings.warehouse_list,
        row_width = 2,
        next_step=warehouse_update_step_3
    )

@cancelDecorator
def warehouse_update_step_3(message):
    try:
        if not message.text in settings.warehouse_list: raise exceptions.WarehouseElementTypeException
        dbOperator.notes[message.from_user.id] =\
            dbOperator.WarehouseElemNote.create_warehouse_elem_note(message.from_user.id, message.text)
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.warehouse_elem_count_request(message.text),
            next_step=warehouse_update_step_4
        )
    except exceptions.WarehouseElementTypeException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="На складе нет такой позиции!",
            next_step=warehouse_update_step_3,
            buttons_list = settings.warehouse_list,
            row_width = 2,
        )

@cancelDecorator
def warehouse_update_step_4(message):
    try:
        dbOperator.notes[message.from_user.id]['count'] = int(message.text)
        dbOperator.WarehouseElemNote.writeInDB(dbOperator.notes.pop(message.from_user.id))
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Складская позиция обновлена!",
            buttons_list=["Ок"],
            withoutCancel=True,
        )
    except ValueError:
            reply_with_buttons(
                chat_id=message.chat.id,
                text=settings.int_value_error_message,
                next_step=warehouse_update_step_4
            )

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
#       ПОЛУЧЕНИЕ ИСТОРИИ ОБСЛУЖИВАНИЯ ПРИНТЕРА
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["printer_story"])
@cancelDecorator
def show_printer_story_step1(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text="Введи номер принтера",
        next_step=show_printer_story_step2
    )

@cancelDecorator
def show_printer_story_step2(message):
    try:
        story = dbOperator.DBOperator.getPrinterStory(int(message.text))
        if len(story["res"]) == 0: raise exceptions.StoryPrinterLengthException
        text = table_notes_msg_view(f"История принтера №{message.text}", story["field_names"], story["res"])
        reply_with_buttons(
            chat_id=message.chat.id,
            text= text,
            buttons_list=["Смотреть историю другого принтера"],
            next_step=show_printer_story_step1
        )
    except ValueError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Номер принтера должен быть целым числом, попробуйте ещё раз",
            next_step=show_printer_story_step2
        )
    except exceptions.StoryPrinterLengthException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text= "История принтера пуста.",
            next_step=show_printer_story_step1,
            buttons_list=["Смотреть историю другого принтера"]
        )
    except exceptions.PrinterCountException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=f"Имеющееся количество принтеров: {settings.printer_count}\nПопробуйте ещё раз:",
            next_step=show_printer_story_step2,
        )
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
#       ПОЛУЧЕНИЕ СОДЕРЖАНИЯ СКЛАДА
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________


@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["warehouse"])
def show_warehouse_step1(message):
    warehouse_contents = dbOperator.DBOperator.getWarehouseContents()
    text = list_notes_msg_view("Содержимое склада:", warehouse_contents["field_names"],
                               [x[0] for x in warehouse_contents["res"]])
    reply_with_buttons(
        chat_id=message.chat.id,
        text=text,
        buttons_list=["Ок"],
        withoutCancel=True,
    )

# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
#       СТАРТОВОЕ МЕНЮ
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________

@bot.message_handler()
def handle_start_message(message):
    reply_markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    reply_markup.add(*settings.start_menu_commands.values())
    bot.send_message(
        chat_id=message.chat.id,
        text = "Привет! Чем займёмся?",
        reply_markup=reply_markup
    )


