#!/usr/bin/env python3
'''
Testing writing and reading to DICTIONARY
To get rid of global variables needed
'''
# encoding=utf-8
#
# Variables
#MYTUPLE = 1, 2, 3
#print(MYTUPLE[2])
#from datetime import datetime
#import datetime
import time
import syslog
import logging

MYDICT = {
    'starttime':'',
    'endtime':'',
    'timediff':'',
    'total':''
}

MYDICT['total'] = int(0)
INDEX = 0

# Define logging
syslog.syslog("Starting up RAWPOWER")
#logger = logging.getLogger(__name__)
logger = logging.getLogger('RAWPOWER')
logger.setLevel(logging.INFO)
# Create a File Handler
#filemode='w' == Truncate file to zero length or create text file for writing.
#The stream is positioned at the beginning of the file.
handler = logging.FileHandler('/home/pi/steca/rawpower.log', mode='w')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
# End Define Logging -> use logger.info('')

def starttime():
    '''
    Calculation of starttime
    '''
    MYDICT['starttime'] = int(time.time_ns())

def endtime():
    '''
    Calculation of endtime
    '''
    MYDICT['endtime'] = int(time.time_ns())

def calctime():
    '''
    Calculation of time from start and endtime
    '''
    timediff = int(MYDICT['endtime']) - int(MYDICT['starttime'])
    MYDICT['timediff'] = int(timediff / 1000000000)
    MYDICT['total'] = int(MYDICT['timediff']) + int(MYDICT['total'])
    mins, secs = divmod(MYDICT['total'], 60)
    hours, mins = divmod(mins, 60)
    print("{}, {}".format(MYDICT['timediff'], MYDICT['total']))
    logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')

def calctotaltimeon():
    '''
    Calculates how long Vastus has been on
    '''
    mins, secs = divmod(MYDICT['total'], 60)
    hours, mins = divmod(mins, 60)
    print(f'Total Time On Today: {hours:d}:{mins:02d}:{secs:02d}')
    print("Total Time on today: {}:{}:{}".format(hours, mins, secs))
    logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')

while True:
    if INDEX < 15:
        starttime()
        time.sleep(5)
        endtime()
        calctime()
        INDEX = INDEX + 1
    if INDEX == 15:
        exit()
