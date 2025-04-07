import telebot
import settings, exceptions, dataBaseOperator

bot = telebot.TeleBot(settings.API_TOKEN)
dbOperator = dataBaseOperator.DBOperator()
user_inputs = {}

# Сделать препроцесс кнопки "ОТМЕНА"

@bot.message_handler(commands=["start"])
def handle_start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    for item in settings.start_menu_commands: markup.add(telebot.types.KeyboardButton(item))
    bot.send_message(
        chat_id=message.chat.id,
        text = settings.hello_question,
        reply_markup=markup
    )

#       СЦЕНАРИЙ ЗАМЕНЫ КОМПЛЕКТУЮЩЕЙ
@bot.message_handler(func=lambda msg: msg.text==settings.start_menu_commands[0])
def handle_component_replacement(message):
    bot.register_next_step_handler(
        bot.send_message(
            chat_id=message.chat.id,
            text=settings.printer_number_request,
            reply_markup = telebot.types.ReplyKeyboardRemove(),
        ),
        component_replacement_step1
    )

def component_replacement_step1(message):
    try:
        user_inputs[message.from_user.id] = {
            "username": message.from_user.username,
            "printer_number":int(message.text),
            "component":None
        }
        markup = telebot.types.ReplyKeyboardMarkup()
        for item in settings.component_list: markup.add(telebot.types.KeyboardButton(item))
        bot.register_next_step_handler(
            bot.send_message(
                chat_id=message.chat.id,
                text=settings.component_request,
                reply_markup=markup
            ),
            component_replacement_step2
        )
    except ValueError:
        bot.register_next_step_handler(
            bot.send_message(chat_id=message.chat.id, text="Нужно ввести целое число!"),
            component_replacement_step1
        )



def component_replacement_step2(message):
    try:
        if not message.text in settings.component_list: raise exceptions.ComponentException
        user_inputs[message.from_user.id]['component'] = message.text
        dbOperator.addComponentReplaceNote(user_inputs.pop(message.from_user.id))
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
        if message.text == settings.warehouse_update_types[0]: inventory(message)
        elif message.text == settings.warehouse_update_types[1]: warhouse_update_step_2(message)
    # except:
        # print("неизвестная команда")
        # pass



def inventory(message):
    for elem_type in settings.warehouse_list:
        user_inputs[message.from_user.id] = {
            "username": message.from_user.username,
            'element_type':elem_type,
            'count':None
        }
        bot.register_next_step_handler(
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Введите количество позиции [{elem_type}]:",
                reply_markup=telebot.types.ReplyKeyboardRemove()
            ),
            writeInDB
        )
    dbOperator.inventory_end()

def writeInDB(message):
    try:
        user_inputs[message.from_user.id]['component'] = int(message.text)
        dbOperator.updateWarehouseElement(user_inputs.pop(message.from_user.id))
    except ValueError:
        bot.register_next_step_handler(
            bot.send_message(chat_id=message.chat.id, text="Нужно ввести целое число!"),
            writeInDB
        )


def warhouse_update_step_2(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    for item in settings.warehouse_list: markup.add(telebot.types.KeyboardButton(item))
    bot.register_next_step_handler(
        bot.send_message(
            chat_id=message.chat.id,
            text = settings.warehouse_element_type_request,
            reply_markup = markup),
        warhouse_update_step_3
    )

def warhouse_update_step_3(message):
    try:
        if not message.text in settings.warehouse_list: raise exceptions.WarehouseElementTypeException
        user_inputs[message.from_user.id] = {
            "username": message.from_user.username,
            "element_type": message.text,
            "count": None
        }
        bot.register_next_step_handler(
            bot.send_message(
                chat_id=message.chat.id,
                text=f"Введите количество позиции [{message.text}]:",
                reply_markup = telebot.types.ReplyKeyboardRemove(),
            ),
            warhouse_update_step_4
        )
    except exceptions.WarehouseElementTypeException:
        bot.send_message(chat_id=message.chat.id, text="На складе нет такой позиции!"),
def warhouse_update_step_4(message):
    try:
        user_inputs[message.from_user.id]['count'] = int(message.text)
        dbOperator.updateWarehouseElement(user_inputs.pop(message.from_user.id))
        bot.send_message(chat_id=message.chat.id, text="Готово"),
    except ValueError:
        bot.register_next_step_handler(
            bot.send_message(chat_id=message.chat.id, text="Нужно ввести целое число"),
            warhouse_update_step_4
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