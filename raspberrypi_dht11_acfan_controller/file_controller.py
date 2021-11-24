import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('file_controller')

''' 
Basic File Reader/Writer per line
'''


def lettura():
    try:
        righe = []
        with open('status.txt', 'r') as f:
            righe = f.readlines()
        logger.info(f"Correct read")
        return righe

    except Exception as e:
        print()
        logger.error(f"Error reading file")
        logger.error(e)


def scrittura(stato, data):
    try:

        with open('status.txt', 'w') as f:
            f.write("{0}\n{1}".format(stato, data))
        logger.info(f"Correct write")

    except Exception as e:
        print()
        logger.error(f"Error writing file")
        logger.error(e)


'''
# testing area 
# main 
stringa = []

stringa = lettura()
print(stringa[0])
print (stringa[1])

scrittura(stato = "False", data = "1970-01-01 01:00:00")

#for i in stringa:
#    print(i)
scrittura(stato = "False", data = "23456543")
'''
