import os
import signal
import remote.key as keys
import logging
import sys

from os import path
from telegram.ext import updater
from telegram.ext import *
from datetime import date, datetime, timedelta


# Import our packet

from relay.relay_controller import relay_off, relay_on


# Setting right logger

logger = logging.getLogger('telegram_bot')


# ""TEXT ONLY"" commands

def help_command(update, context):
    logger.info("Called HELP")
    update.message.reply_text("/status \n /off \n /on <seconds  >)")


def sample_responses(input_text):
    user_message = str(input_text).lower()
    if user_message in ("hello", "hi", "sup", "ciao"):
        return "Welcome :)"

    if user_message in ("Who made this Project?", "Who made this project", "Who are the creators", "Who are the creators?", "creator"):
        return "Ettore S. & Stiven S."

    return "Idk what are you saying"


# ""ON OVERRIDE"" Command

def on_command(update, context):
    logger.info("Called ON")

    # Getting on_time from user (default 20s)

    if(" ".join(context.args) == ""):
        user_says = "20"
    else:
        user_says = " ".join(context.args)

    update.message.reply_text("You said: " + user_says)

    # Getting IRT data from Fifo Queue ( dato[0]: Boolean fan status, dato[1]: expected shut down (Unix datetime format))

    dato = q1.get()

    awake = int(user_says)

    if dato[0] == True:
        # If it's ON -> update off time
        logger.debug("Updating OFF Time")

        dato[1] = dato[1] + timedelta(0, awake)

        update.message.reply_text("ON + Time added")
    else:
        # Turn ON
        logger.debug("Turning ON Fan")

        relay_on()

        dato[1] = datetime.now() + timedelta(0, awake)
        update.message.reply_text("Turned ON")

    q1.put(dato)

# ""OFF OVERRIDE"" Command

def off_command(update, context):
    logger.info("Called OFF")

    # Getting IRT data from Fifo Queue 
    dato = q1.get()
    # update.message.reply_text("%s" %str(dato))
    if dato[0] == True:
        # If it's ON -> override
        logger.debug("Overriding OFF")
        dato[1] = datetime.fromtimestamp(0)
        dato[0] = False

        relay_off()   
        update.message.reply_text("OFF")
    else:
        # It's already OFF, do nothing
        logger.debug("Doing nothing -> Fan is already off")
        update.message.reply_text("Is Already OFF")

    q1.put(dato)

# ""STATUS"" Command

def status_command(update, context):
    logger.info("Called Status")
    
    dato = q1.get()
    q1.put(dato)
    update.message.reply_text(str(dato[0]) + str(dato[1]))


def handler_message(update, context):
    text = str(update.message.text).lower()
    response = sample_responses(text)
    update.message.reply_text(response)


def error(update, context):
    logger.error("Error")
    logger.error(update)
    logger.error(context.error)


def run_bot(q):
    logger.debug("Bot started")

    # not ideal - global variable: threads fifo queue

    global q1
    q1 = q

    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("on", on_command))
    dp.add_handler(CommandHandler("off", off_command))
    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("help", help_command))

    dp.add_handler(MessageHandler(Filters.text, handler_message))
    dp.add_error_handler(error)

    updater.start_polling(0)  # checking user inputs(time)
    # print("bot ready")
    # Idling BOT
    # used for gentle shutdown procedure
    # updater.idle()

    updater.idle(stop_signals=(signal.SIGINT, signal.SIGTERM))
    logger.info("Shutting Down Initialized")
    logger.debug("Sending Signal SIGUSR1")
    os.kill(os.getpid(), signal.SIGUSR1)
    # print("BOT KILLED")

