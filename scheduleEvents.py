import schedule
import time
import dbOperator
import settings
import TgBot
import datetime

def mainScheduleFunction():
    try:
        print("Запуск отслеживания расписания событий...")

        # ДОПИСАТЬ ОПРЕДЕЛЕНИЕ ЧАСОВОГО ПОЯСА
        schedule.every().thursday.at("08:00").do(inventory_notificatioin)
        schedule.every().thursday.at("09:00").do(inventory_notificatioin)
        schedule.every().thursday.at("10:00").do(inventory_notificatioin)

        schedule.every().friday.at("08:00").do(inventory_notificatioin)
        schedule.every().friday.at("09:00").do(inventory_notificatioin)
        schedule.every().friday.at("10:00").do(inventory_notificatioin)

        schedule.every().day.at("05:00").do(sendReservDBCopy)

        schedule.every().day.at("06:00").do(purchase_necessity_notificatioin)

        print("Расписание событий запущено")
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        print("schedule finished")

def inventory_notificatioin():
    count = len(dbOperator.DBOperator.getInventoryNeedsPositions())
    mainChatID = settings.main_chat_id

    if count > 0:
        text = f"Напоминание провести инвентаризацию. Необходимо обновление {count} позиций"
        TgBot.reply_with_buttons(chat_id=mainChatID, text=text)

def purchase_necessity_notificatioin():
    responsibles = dbOperator.DBOperator.getResponsiblePosiotion()
    for id in responsibles.keys():
        text = "Запасы на исходе, Милорд!\nНеобходимо закупить:\n\n"
        TgBot.reply_with_buttons(chat_id=id, text=text+"\n".join(responsibles[id]))

def sendReservDBCopy():
    TgBot.bot.send_document(
        settings.adminID,
        open(settings.dbPath, 'rb'),
        disable_notification=True,
        visible_file_name=" ".join([datetime.datetime.now().strftime("%d.%m.%y"), settings.dbName]),
    )
