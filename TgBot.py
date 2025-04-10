import telebot
import settings, exceptions, dbOperator

bot = telebot.TeleBot(settings.API_TOKEN)
bot.delete_webhook()

def reply_with_buttons(chat_id, text, buttons_list=None, next_step=None):
    if not buttons_list: reply_markup = telebot.types.ReplyKeyboardMarkup()
    else:
        reply_markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
        for item in buttons_list: reply_markup.add(telebot.types.KeyboardButton(item))
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

# Сделать препроцесс кнопки "ОТМЕНА"




#       СЦЕНАРИЙ ЗАМЕНЫ КОМПЛЕКТУЮЩЕЙ
@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands[0])
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


        dbOperator.addComponentReplaceNote(dbOperator.notes.pop(message.from_user.id))
    except exceptions.ComponentException:
        bot.send_message(chat_id=message.chat.id, text="Введено неизвестное имя компонента"),

#       СЦЕНАРИЙ ОБНОВЛЕНИЯ СКЛАДА

@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands[1])
def handle_warehouse_update(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text="Что будем делать?",
        next_step=warhouse_update_step_1,
        buttons_list=settings.warehouse_update_types
    )

def warhouse_update_step_1(message):
    if message.text == settings.warehouse_update_types[0]: inventory_start(message)
    elif message.text == settings.warehouse_update_types[1]: warhouse_update_step_2(message)
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
        dbOperator.WarehouseElemNote.create_warehouse_elem_note(message.from_user.username, elem_type)
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















def warhouse_update_step_2(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text=settings.warehouse_element_type_request,
        buttons_list=settings.warehouse_list,
        next_step=warhouse_update_step_3
    )

def warhouse_update_step_3(message):
    try:
        if not message.text in settings.warehouse_list: raise exceptions.WarehouseElementTypeException
        dbOperator.notes[message.from_user.id] =\
            dbOperator.WarehouseElemNote.create_warehouse_elem_note(message.from_user.username, message.text)
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.warehouse_elem_count_request(message.text),
            next_step=warhouse_update_step_4
        )
    except exceptions.WarehouseElementTypeException:
        reply_with_buttons(
            chat_id=message.chat.id,
            text=settings.warehouse_elem_undef,
            next_step=warhouse_update_step_3
        )

def warhouse_update_step_4(message):
    try:
        dbOperator.notes[message.from_user.id]['count'] = int(message.text)
        dbOperator.WarehouseElemNote.writeInDB(message)
        reply_with_buttons(chat_id=message.chat.id, text=settings.success_msg)
    except ValueError:
            reply_with_buttons(
                chat_id=message.chat.id,
                text=settings.int_value_error_message,
                next_step=warhouse_update_step_4
            )






# @bot.message_handler()
# def handle_get_logs(message):
#     markup = telebot.types.ReplyKeyboardRemove()
#     pass

@bot.message_handler()
def handle_start_message(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text = settings.hello_question,
        buttons_list=settings.start_menu_commands
    )


bot.infinity_polling()