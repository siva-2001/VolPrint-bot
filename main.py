from TgBot import bot
import threading
from scheduleEvents import mainScheduleFunction

if __name__ == "__main__":
    thread = threading.Thread(target=mainScheduleFunction)
    thread.start()
    bot.infinity_polling()