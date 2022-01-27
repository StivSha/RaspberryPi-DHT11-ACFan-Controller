"""Main module."""
import os
# print(os.getpid())
import queue
import signal
import threading
import logging
import logging.config

from os import kill
from threading import Thread

# Import our packets
print("importing your libraries")

from bot import run_bot
from fan_caller import DHT11_Fan_caller

print("done!")

# Logger setup

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('MAIN')



# ""MAIN""

def start():
    # SIGUSR1 handler. Used to gently kill thread 1 when SIGINT or SIGTERM are called
    # SIGUSR1 is sent from bot
    print("starting")
    def sigusr1_handler(*args):
        logger.debug(
            "Signal SIGUSR1 Received - Killing DHT11_Fan_caller process ")
        print("signal received")
        pill2kill.set()

        # wait for t1 to end
        t1.join()

        # kill the rest of the program
        logger.debug("Killing main module")
        kill(os.getpid(), signal.SIGTERM)

    signal.signal(signal.SIGUSR1, sigusr1_handler)

    pill2kill = threading.Event()
    q = queue.Queue()

    t1 = Thread(target=DHT11_Fan_caller, args=(q, pill2kill))
    t1.start()
    run_bot(q)

if __name__ == '__main__':
    logger.debug("__name__ == __main__ STARTING program")
    start()
