import RPi.GPIO as GPIO
import time
import datetime
import os
import subprocess
import json
import smtplib
import logging
from email.message import EmailMessage

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
    "varfile": '/home/pi/steca/variables.json',
    "rawlog": '/home/pi/steca/rawpower1.log',
    "timediff": '',
    "total": int(0),
    "email": "ai@iki.fi",
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

#logger = logging.getLogger(__name__)
logger = logging.getLogger('RAWPOWER')
logger.setLevel(logging.INFO)
# Create a File Handler
#filemode='w' == Truncate file to zero length or create text file for writing.
#The stream is positioned at the beginning of the file.
handler = logging.FileHandler(MYDICT["rawlog"], mode='w')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
# End Define Logging -> use logger.info('')

#  Tämä formaattin toimii
#print(f'Teho on: {MYDICT["teho"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')

def send_email():
    # Open the plain text file whose name is in textfile for reading.
    with open(MYDICT['rawlog']) as fp:
        # Create a text/plain message
        msg = EmailMessage()
        msg.set_content(fp.read())
    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = f'Daily {MYDICT["rawlog"]}'
    msg['From'] = MYDICT["email"]
    msg['To'] = MYDICT["email"]
    
    # Send the message via our own SMTP server.
    s = smtplib.SMTP('smtp.kolumbus.fi')
    s.send_message(msg)
    logger.info(f'Email has been sent to {MYDICT["email"]}')
    s.quit()
    #logger.info(f'Email has been sent to {MYDICT["email"]}')
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
    timediff = int(MYDICT['endtime']) - int(MYDICT['starttime'])
#    print(timediff)
    MYDICT['timediff'] = int(timediff / 1000000000)
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
    #print("Total Time on today: {}:{}:{}".format(hours, mins, secs))
    logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')
for i in range(0, 2):
    starttime()
    time.sleep(10)
    endtime()
    calctime()
calctotaltimeon()
#send_email()
