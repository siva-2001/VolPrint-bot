import telebot
import settings, exceptions, dataBaseOperator

bot = telebot.TeleBot(settings.API_TOKEN)
dbOperator = dataBaseOperator.DBOperator()
user_inputs = {}

@bot.message_handler(commands=["start"])
def handle_start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
    for item in settings.start_menu_commands:
        markup.add(telebot.types.KeyboardButton(item))
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
    except ValueError: bot.send_message(chat_id=message.chat.id, text="Нужно ввести целое число!")

def component_replacement_step2(message):
    try:
        if not message.text in settings.component_list: raise exceptions.ComponentException
        user_inputs[message.from_user.id]['component'] = message.text
        dbOperator.addComponentReplaceNote(user_inputs.pop(message.from_user.id))
    except exceptions.ComponentException:
        bot.send_message(chat_id=message.chat.id, text="Введено неизвестное имя компонента"),


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