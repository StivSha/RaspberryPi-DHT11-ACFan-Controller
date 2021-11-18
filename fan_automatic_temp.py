import time
from datetime import date, datetime, timedelta
from file_controller import lettura, scrittura
from relay_controller import relay_off, relay_on
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('fan_auto')

'''
FUNZIONA 2.0 alpha
'''


def turn_on(awake_time):
    # print("Acceso")
    logger.debug("Turning ON fan")
    relay_on()
    # print("     turn on time: " + str(datetime.now()) + " turn off time: " + str(datetime.now() + timedelta(0, awake_time)))
    return (datetime.now() + timedelta(0, awake_time))


def turn_off():
    # print("Spento")
    logger.debug("Turning OFF fan")
    relay_off()
    return (datetime.fromtimestamp(0))


def set_status(status, awake_time=8):
    data = []
    data = lettura()
    power_off_time = datetime.fromisoformat(data[1])
    actual_status = True

    if data[0] == "True\n":
        actual_status = True
        # print(actual_status)
    elif data[0] == "False\n":
        actual_status = False
        # print(actual_status)
    else:
        logger.critical("data[0] not Boolean")
        logger.critical("Exiting")
        exit(1)
    # TODO SYSTEM CALL SIG INT

    if (power_off_time < datetime.now()) & (actual_status == True):
        # spegni
        logger.info("time elapsed, turning off")
        power_off_time = turn_off()
        status = False
        scrittura(stato=status, data=power_off_time)

    else:
        # print("Stato attuale: " + str(actual_status) + " Stato: " + str(status))
        if (actual_status == False) & (status == True):
            # se e' spento e lo voglio accendere
            power_off_time = turn_on(awake_time)
            status = True
            scrittura(stato=status, data=power_off_time)


'''
print("Test 1 - PASSEd")
print(" 1")
set_status(status = True, awake_time=100)
time.sleep(2)
print(" 2")
set_status(status = True)
time.sleep(6)
print(" 3")
set_status(status = True)
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
