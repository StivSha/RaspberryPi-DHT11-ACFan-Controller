import key as keys
import responses as R
import logging
import logging.config
from telegram.ext import updater
from telegram.ext import *
from datetime import date, datetime, timedelta
from file_controller import lettura, scrittura
from relay_controller import relay_off, relay_on


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('telegram_bot')

logger.debug("Bot started")


def help_command(update, context):
    logger.info("Called HELP")
    update.message.reply_text("/status \n /off \n /on <seconds  >)")

# ON OVERRIDE


def on_command(update, context):
    logger.info("Called ON")

    if(" ".join(context.args) == ""):
        user_says = "20"
    else:
        user_says = " ".join(context.args)

    update.message.reply_text("You said: " + user_says)
    dato = []
    dato = lettura()
    awake = int(user_says)
    power_off_time = datetime.fromisoformat(dato[1])

    if dato[0] == "True\n":
        # If it's ON -> update off time
        logger.debug("Updating OFF Time")
        scrittura(stato=True, data=power_off_time + timedelta(0, awake))
        # print("Funzione ON (Aggiunta di tempo ")
        update.message.reply_text("ON + Aggiunta Tempo")
    else:
        # Turn ON
        logger.debug("Turning ON Fan")
        relay_on()
        # print("Funzione ON")
        update.message.reply_text("ON")
        scrittura(stato=True, data=datetime.now() + timedelta(0, awake))

# OFF OVERRIDE


def off_command(update, context):
    logger.info("Called OFF")
    dato = []
    dato = lettura()
    if dato[0] == "True\n":
        # If it's ON -> override
        logger.debug("Overriding OFF")
        scrittura(stato=False, data=datetime.fromtimestamp(0))
        relay_off()
        # print("Funzione OFF")
        update.message.reply_text("OFF")
    else:
        # It's already OFF, do nothing
        logger.debug("Doing nothing -> Fan is already off")
        # print("Era gia' OFF")
        update.message.reply_text("Is Already OFF")


def status_command(update, context):
    logger.info("Called Status")
    dato = []
    dato = lettura()
    # print("Funzione STATUS")
    # print(dato[0] + dato[1])
    update.message.reply_text(dato[0] + dato[1])


def handler_message(update, context):
    text = str(update.message.text).lower()
    response = R.sample_responses(text)
    update.message.reply_text(response)


def error(update, context):
    logger.error("Error")
    logger.error(update)
    logger.error(context.error)
    # print("Update {update} caused error {context.error}")


def main():
    logger.debug("Main called")
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("on", on_command))
    dp.add_handler(CommandHandler("off", off_command))
    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(MessageHandler(Filters.text, handler_message))
    dp.add_error_handler(error)

    updater.start_polling(0)  # checking user inputs(tempo)
    updater.idle()


main()
