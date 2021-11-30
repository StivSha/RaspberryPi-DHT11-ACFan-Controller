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
        #print("status=%s, data=%s" %(status, actual[1]))
        #scrittura(stato=status, data=actual[1])

    # returning updated status and off time
    
    return [status, actual[1]]


'''
attuale = [False, datetime.fromtimestamp(0)]
print("Test 1 - PASSEd")
print(" 1")
attuale = set_status(status = True, actual=attuale,  awake_time=1)
time.sleep(5)
print(" 2")
attuale = set_status(status = True, actual=attuale)
time.sleep(6)
print(" 3")
attuale = set_status(status = True, actual=attuale)
'''
'''
print("Test 2")
print("1    " + str(datetime.now()))
set_status(status = False)
time.sleep(2)
print("2    " + str(datetime.now()))
set_status(status = True)
print("3    " + str(datetime.now()))
set_status(status = False)
time.sleep(1)
print("4    " + str(datetime.now()))
set_status(status = True)
time.sleep(9)
print("5    " + str(datetime.now()))
set_status(status = False)
'''
