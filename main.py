from TgBot import bot
import threading, sys
import settings
from scheduleEvents import mainScheduleFunction
import dbInitSQL

if __name__ == "__main__":
    if isinstance(settings.API_TOKEN, type(None)):
        print("API-токен отсутствует в среде окружения")
        sys.exit()
    dbInitSQL.dbInitial()
    thread = threading.Thread(target=mainScheduleFunction)
    thread.start()
    bot.infinity_polling()