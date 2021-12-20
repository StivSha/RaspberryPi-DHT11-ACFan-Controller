import os
import signal
import logging
from datetime import date, datetime, timedelta
from relay.relay_controller import relay_off, relay_on


# Import our packet

logger = logging.getLogger('fan_auto')

'''
# Works 5.0 alpha
'''


def turn_on(awake_time):
    logger.debug("Turning ON fan")
    relay_on()

    return (datetime.now() + timedelta(0, awake_time))


def turn_off():
    logger.debug("Turning OFF fan")
    relay_off()

    return (datetime.fromtimestamp(0))


def set_status(status, actual, awake_time=8):

    # Check actual[0] is boolean

    if type(actual[0]) is not bool:
        logger.critical("actual[0] not Boolean")
        logger.critical("Exiting")
        logger.debug("Calling SIGTERM")

        os.kill(os.getpid(), signal.SIGTERM)

    # if shutdown time has elapsed and fan is still ON

    if (actual[1] < datetime.now()) & (actual[0] == True):
        # TURN OFF
        logger.info("time elapsed, turning off")

        actual[1] = turn_off()
        status = False

    elif (actual[0] == False) & (status == True):
        # if it's off and I want it ON
        logger.info("turn on called")

        actual[1] = turn_on(awake_time)
        status = True
    # returning updated status and off time

    return [status, actual[1]]
