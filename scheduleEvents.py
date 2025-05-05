import schedule
import time
import dbOperator
import settings
import TgBot
import datetime
import telebot

def mainScheduleFunction():
    try:
        print("Запуск отслеживания расписания событий...")

        # ДОПИСАТЬ ОПРЕДЕЛЕНИЕ ЧАСОВОГО ПОЯСА
        schedule.every().tuesday.at("06:00").do(inventory_notificatioin)
        schedule.every().friday.at("06:00").do(inventory_notificatioin)
        schedule.every().day.at("02:00").do(sendReservDBCopy)

        schedule.every().monday.at("04:00").do(purchase_necessity_notificatioin)
        schedule.every().thursday.at("04:00").do(purchase_necessity_notificatioin)
        schedule.every().wednesday.at("04:00").do(purchase_necessity_notificatioin)
        schedule.every().tuesday.at("04:00").do(purchase_necessity_notificatioin)
        schedule.every().friday.at("04:00").do(purchase_necessity_notificatioin)

        print("Расписание событий запущено")
        while True:
            schedule.run_pending()
            time.sleep(1)

    finally: print("schedule finished")

def inventory_notificatioin():
    count = len(dbOperator.DBOperator.getInventoryNeedsPositions())
    if count > 0:
        TgBot.bot.send_message(
            chat_id=settings.main_chat_id,
            text=f"Напоминание провести инвентаризацию. Необходимо обновление {count} позиций",
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )

def purchase_necessity_notificatioin():
    responsibles = dbOperator.DBOperator.getResponsiblePosiotion()
    for id in responsibles.keys():
        text = "Запасы на исходе, Милорд!\nНеобходимо закупить:\n\n"
        TgBot.reply_with_buttons(chat_id=id, text=text+"\n".join(responsibles[id]))

def sendReservDBCopy():
    for userID in dbOperator.DBOperator.getAdmins():
        TgBot.bot.send_document(
            userID[0],
            open(settings.dbPath, 'rb'),
            disable_notification=True,
            visible_file_name=" ".join([datetime.datetime.now().strftime("%d.%m.%y"), settings.DBName]),
        )
