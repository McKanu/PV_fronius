import RPi.GPIO as GPIO
import time
import datetime
import os
import subprocess
import json

Rele1 = 26
Rele2 = 20
Rele3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Rele1,GPIO.OUT)
GPIO.output(Rele1,GPIO.HIGH) #Vastus ei ole päällä

with open('/home/pi/steca/variables.json') as f:
    variables = json.load(f)

MYDICT = {
    "starttime": '',
    "endtime": '',
    "timediff": '',
    "total": int(0),
    "counter1": '',
    "counter1": '',
    "counter2": '',
    "counter3": '',
    "counter4": '',
    "counter5": '',
    "power": "",
    "teho": variables['power'],
    "start": variables['start'],
    "stop": variables['stop']
}

#  Tämä formaattin toimii
#print(f'Teho on: {MYDICT["teho"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')

def starttime():
    '''
    Calculation of starttime
    '''
    MYDICT['starttime'] = int(time.time_ns())
    print(MYDICT['starttime'])
def endtime():
    '''
    Calculation of endtime
    '''
    MYDICT['endtime'] = int(time.time_ns())
    print(MYDICT['endtime'])
def calctime():
    '''
    Calculation of time from start and endtime
    '''
    timediffint = MYDICT['endtime'] - MYDICT['starttime']
#    print(timediff)
    MYDICT['timediff'] = int(timediffint / 1000000000)
    MYDICT['total'] = int(MYDICT['timediff']) + int(MYDICT['total'])
    mins, secs = divmod(MYDICT['total'], 60)
    hours, mins = divmod(mins, 60)
    print("{}, {}".format(MYDICT['timediff'], MYDICT['total']))
    #logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')
def calctotaltimeon():
    '''
    Calculates how long Vastus has been on
    '''
    mins, secs = divmod(MYDICT['total'], 60)
    hours, mins = divmod(mins, 60)
    print(f'Total Time On Today: {hours:d}:{mins:02d}:{secs:02d}')
    print("Total Time on today: {}:{}:{}".format(hours, mins, secs))
    #logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')

for i in range(0, 3):
    starttime()
    time.sleep(10)
    endtime()
    calctime()
calctotaltimeon()
