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

@bot.message_handler(commands=["start"])
def handle_start_message(message):
    reply_with_buttons(
        chat_id=message.chat.id,
        text = settings.hello_question,
        buttons_list=settings.start_menu_commands
    )


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
        dbOperator.ReplacementNote.create_component_replacement_note(message)
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
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    for item in settings.warehouse_update_types: markup.add(telebot.types.KeyboardButton(item))
    bot.register_next_step_handler(
        bot.send_message(
            chat_id=message.chat.id,
            text="Что будем делать?",
            reply_markup = markup),
        warhouse_update_step_1
    )

def warhouse_update_step_1(message):
    # try:
        if message.text == settings.warehouse_update_types[0]: inventory_start(message)
        elif message.text == settings.warehouse_update_types[1]: warhouse_update_step_2(message)
    # except:
        # print("неизвестная команда")
        # pass



def inventory_start(message):
    pos_list = list(settings.warehouse_list)
    dbOperator.notes[message.message.from_user.id] = {

    }
    print(pos_list)

def inventory_circle(message): pass


def inventory_end(message):
    pos_list = list(settings.warehouse_list)
    print(pos_list)
    dbOperator.inventory_end()















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
        dbOperator.WarehouseElemNote.create_warehouse_elem_note(message)
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
        # dbOperator.updateWarehouseElement(user_inputs.pop(message.from_user.id))
        reply_with_buttons(chat_id=message.chat.id, text=settings.success_msg)
    except ValueError:
            reply_with_buttons(
                chat_id=message.chat.id,
                text=settings.int_value_error_message,
                next_step=warhouse_update_step_4
            )











@bot.message_handler(commands=["start"])
def handle_get_logs(message):
    markup = telebot.types.ReplyKeyboardRemove()
    pass

@bot.message_handler()
def handle_start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.add(telebot.types.KeyboardButton("/start"))
    bot.send_message(
        message.chat.id,
        text="Сообщение не распознано, для начала работы нажмите на кнопку START",
        reply_markup=markup
    )

bot.infinity_polling()