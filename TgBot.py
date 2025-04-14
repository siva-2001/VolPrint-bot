import telebot
import settings, exceptions, dbOperator

bot = telebot.TeleBot(settings.API_TOKEN, parse_mode="HTML")


def table_notes_msg_view(title, param_names, param_list):
    param_names = [name.join(["<b>", "</b>"]) for name in param_names]
    text = title + "\n\n"
    for el in param_list:
        param_iterator = zip(param_names, list(el))
        str_list = list()
        for param in param_iterator: str_list.append(" ".join(param))
        text = text + "\n".join(str_list) + "\n\n"
    return text

def reply_with_buttons(chat_id, text, buttons_list=None, next_step=None, row_width=1):

    if not buttons_list: reply_markup = telebot.types.ReplyKeyboardRemove()
    else:
        reply_markup = telebot.types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True, one_time_keyboard=True)
        reply_markup.add(*buttons_list)
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

#       СЦЕНАРИЙ ЗАМЕНЫ КОМПЛЕКТУЮЩЕЙ
@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["comp_replacement"])
def handle_component_replacement(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text=settings.printer_number_request,
        next_step=component_replacement_step1,
    )

def component_replacement_step1(message):
    try:
        dbOperator.notes[message.from_user.id] = dbOperator.ReplacementNote.get_component_replacement_note(message)
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.component_request,
            next_step=component_replacement_step2,
            buttons_list=settings.component_list
        )
    except ValueError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.int_value_error_message,
            next_step=component_replacement_step1,
        )

def component_replacement_step2(message):
    try:
        if not message.text in settings.component_list: raise exceptions.ComponentException
        dbOperator.notes[message.from_user.id]['component'] = message.text
        dbOperator.ReplacementNote.writeInDB(message)
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.success_msg,
        )
    except exceptions.ComponentException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text="Введено неизвестное имя компонента",
            next_step=component_replacement_step2,
        ),

#       СЦЕНАРИЙ ОБНОВЛЕНИЯ СКЛАДА

@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["warehouse_update"])
def handle_warehouse_update(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text="Что будем делать?",
        next_step=warhouse_update_step_1,
        buttons_list=settings.warehouse_update_types
    )

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

def inventory_start(message):
    dbOperator.notes[message.from_user.id] = dbOperator.InventoryNote.create_inventory_note(message)
    elem_type = dbOperator.notes[message.from_user.id]["posList"].pop(0)
    dbOperator.notes[message.from_user.id]["whElemNotes"].append(
        dbOperator.WarehouseElemNote.create_warehouse_elem_note(message.from_user.id, elem_type)
    )
    reply_with_buttons(
        chat_id=message.chat.id,
        text=settings.warehouse_elem_count_request(elem_type),
        buttons_list=None,
        next_step=inventory_circle
    )

def inventory_circle(message):
    try:
        elem_type = dbOperator.notes[message.from_user.id]["posList"].pop(0)
        dbOperator.InventoryNote.writeElemValue(
            user_id=message.chat.id,      username=message.from_user.username,
            count=message.text,           elem_type=elem_type
        )
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.warehouse_elem_count_request(elem_type),
            next_step=inventory_circle
        )


    except ValueError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.int_value_error_message,
            next_step=inventory_circle,
        )
    except IndexError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.inventory_end_message,
            buttons_list=["Ок"]
        )
        inventory_end(message)

def inventory_end(message):
    print(dbOperator.notes[message.from_user.id])
    dbOperator.InventoryNote.end()

def warehouse_update_step_2(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text=settings.warehouse_element_type_request,
        buttons_list=settings.warehouse_list,
        row_width = 2,
        next_step=warehouse_update_step_3
    )

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
            text=settings.warehouse_elem_undef,
            next_step=warehouse_update_step_3
        )

def warehouse_update_step_4(message):
    try:
        dbOperator.notes[message.from_user.id]['count'] = int(message.text)
        dbOperator.WarehouseElemNote.writeInDB(message)
        reply_with_buttons(chat_id=message.chat.id, text=settings.success_msg)
    except ValueError:
            reply_with_buttons(
                chat_id=message.chat.id,
                text=settings.int_value_error_message,
                next_step=warehouse_update_step_4
            )

#       ПОЛУЧЕНИЕ ИСТОРИИ ОБСЛУЖИВАНИЯ ПРИНТЕРА

@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["printer_story"])
def show_printer_story_step1(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text=settings.printer_number_request,
        next_step=show_printer_story_step2
    )

def show_printer_story_step2(message):
    try:
        story = dbOperator.DBOperator.getPrinterStory(int(message.text))
        text = table_notes_msg_view(f"История принтера №{message.text}", story["field_names"], story["res"])
        reply_with_buttons(
            chat_id=message.chat.id,
            text= text
        )
    except ValueError:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.int_value_error_message,
            next_step=show_printer_story_step2
        )
    except telebot.apihelper.ApiTelegramException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text= "История принтера пуста"
        )

@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands["warehouse"])
def show_warehouse_step1(message):
    warehouse_contents = dbOperator.DBOperator.getWarehouseContents()
    text = table_notes_msg_view("Содержимое склада:", warehouse_contents["names"], warehouse_contents["counts"])
    reply_with_buttons(
        chat_id=message.chat.id,
        text=text,
    )

@bot.message_handler()
def handle_start_message(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text = settings.hello_question,
        buttons_list=settings.start_menu_commands.values(),
    )




bot.infinity_polling()