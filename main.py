from TgBot import bot
import threading
from scheduleEvents import mainScheduleFunction
import dbInitSQL

if __name__ == "__main__":
    try:
        dbInitSQL.dbInitial()
        thread = threading.Thread(target=mainScheduleFunction)
        thread.start()
        bot.infinity_polling()
    except TypeError:
        print("API-токен отсутствует в среде окружения")