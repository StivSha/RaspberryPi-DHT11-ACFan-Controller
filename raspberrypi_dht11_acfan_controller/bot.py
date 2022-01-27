import os
import signal
import remote.key as keys
#import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, timedelta

# Import our packet
from relay.relay_controller import relay_off, relay_on

# Setting right logger
#logger = logging.getLogger('telegram_bot')

# ""TEXT ONLY"" commands


def help_command(update, context):
    '''/help, lists available commands'''

    #logger.info("Called HELP")
    update.message.reply_text("/status \n /off \n /on <seconds  >)")


def sample_responses(input_text):
    '''Answers to default text as
    "hello", "hi", "sup", "ciao";
    "Who made this Project?", "Who made this project", "Who are the creators", "Who are the creators?", "creator"
    '''

    user_message = str(input_text).lower()
    if user_message in ("hello", "hi", "sup", "ciao"):
        return "Welcome :)"

    if user_message in ("Who made this Project?", "Who made this project", "Who are the creators", "Who are the creators?", "creator"):
        return "Ettore S. & Stiven S."

    return "Idk what are you saying"


def on_command(update, context):
    '''
    ON_OVERRIDE turns on the fan for x seconds (default 20)
    Gets on_time from user, reads threads queue (q1) and gets 
    dato[0]: Boolean fan status; 
    dato[1]: expected shut down (Unix datetime format);
    if fan is already on it only add on_time to it's "countdown", else
    turns it on for x seconds.
    Turn off time and status are put on the queue
    '''
    #logger.info("Called ON")

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
        #logger.debug("Updating OFF Time")

        # Updating Queue infos (turnoff time)
        dato[1] = dato[1] + timedelta(0, awake)

        update.message.reply_text("ON + Time added")
    else:
        # Turn ON
        #logger.debug("Turning ON Fan")

        relay_on()

        update.message.reply_text("Turned ON")

        # Updating Queue infos (status and turnoff time)
        dato[0] = True
        dato[1] = datetime.now() + timedelta(0, awake)

    # Putting infos in the queue
    q1.put(dato)


def off_command(update, context):
    '''
    OFF_OVERRIDE
    Gets infos from the queue (q1), if fan is on turns it off, if it's off does nothing.
    Updates 'dato' in the queue
    '''

   #logger.info("Called OFF")

    # Getting IRT data from Fifo Queue
    dato = q1.get()
    # update.message.reply_text("%s" %str(dato))
    if dato[0] == True:
        # If it's ON -> override
        #logger.debug("Overriding OFF")

        relay_off()
        update.message.reply_text("OFF")

        # Updating Queue infos (status and turnoff time)
        dato[0] = False
        dato[1] = datetime.fromtimestamp(0)

    else:
        # It's already OFF, do nothing
        #logger.debug("Doing nothing -> Fan is already off")
        update.message.reply_text("Is Already OFF")

    # Putting infos in the queue
    q1.put(dato)


def status_command(update, context):
    '''Gives irt infos about fan status'''
    #logger.info("Called Status")

    # Read queue
    dato = q1.get()
    # Put back same data
    q1.put(dato)
    # Sends data via Telegram
    update.message.reply_text(str(dato[0]) + str(dato[1]))


def handler_message(update, context):
    '''Telegram message handler'''
    text = str(update.message.text).lower()
    response = sample_responses(text)
    update.message.reply_text(response)


def error(update, context):
    # logger.error("Error")
    # logger.error(update)
    # logger.error(context.error)
    print(1)


def run_bot(q):
    '''bot thread function -> it's a thread in the main function. q = queue
    When sigint or sigterm is received this script kills Telegram's Bot, logs everything and 
    sends sigusr1 to fan_caller.py
    '''
    #logger.debug("Bot started")

    # not ideal - global variable: threads fifo queue

    global q1
    q1 = q

    updater = Updater(keys.API_KEY, use_context=True)

    # connect to telegram's servers
    dp = updater.dispatcher

    # add command handlers
    dp.add_handler(CommandHandler("on", on_command))
    dp.add_handler(CommandHandler("off", off_command))
    dp.add_handler(CommandHandler("status", status_command))
    dp.add_handler(CommandHandler("help", help_command))

    # add message handlers
    dp.add_handler(MessageHandler(Filters.text, handler_message))

    # add error handlers
    dp.add_error_handler(error)

    updater.start_polling(0)  # checking user inputs(time)

    # used for a graceful shutdown
    updater.idle(stop_signals=(signal.SIGINT, signal.SIGTERM))
    #logger.info("Shutting Down Initialized")
    #logger.debug("Sending Signal SIGUSR1")

    # sends sigusr1 -> fan_caller.py graceful shutdown (it has a shutdown procedure to clean GPiO)
    os.kill(os.getpid(), signal.SIGUSR1)
