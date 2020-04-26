import RPi.GPIO as GPIO
import time
import datetime
import os
import subprocess
import json
from bs4 import BeautifulSoup as soup
import requests
import lxml
import syslog
import logging
from logging.handlers import TimedRotatingFileHandler
import smtplib
from email.message import EmailMessage

Rele1 = 26
Rele2 = 20
Rele3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# Alustaa Rele1:n
GPIO.setup(Rele1,GPIO.OUT)
GPIO.output(Rele1,GPIO.HIGH) #Vastus ei ole päällä

# Ladataan muuttujat tiedostosta
#with open('/home/pi/steca/variables.json') as f:
#    variables = json.load(f)

MYDICT = {
    "starttime": int(0),
    "endtime": int(0),
    "timediff": int(0),
    "total": int(0),
    "onTime": '',
    "offTime": '',
    "onoff": '',
    "url": 'http://192.168.10.59/measurements.xml',
    "email": "ai@iki.fi",
    "tunti": '',
    "counter1": '',
    "counter2": '',
    "counter3": '',
    "counter4": '',
    "counter5": '',
    "ctimeinit": '',
    "ctime": '',
    "rawlog": '/home/pi/steca/rawpower.log',
    "varfile": '/home/pi/steca/variables.json',
    "varfile1": '/home/pi/steca/power.json',
    "power": '',
    "teho": '' ,
    "power": '',
    "start": '',
    "stop": ''
}

with open(MYDICT["varfile"]) as f:
    variables = json.load(f)

MYDICT["power"] = int(variables["power"])
MYDICT["start"] = int(variables["start"])
MYDICT["stop"] = int(variables["stop"])
MYDICT['counter1'] = int(0)
MYDICT['counter2'] = int(0)
MYDICT['counter3'] = int(0)
MYDICT['counter4'] = int(0)
MYDICT['counter4'] = int(0)

#-----------------------------------------------------------------------------
# Define logging
syslog.syslog("Starting up RAWPOWER")
#logger = logging.getLogger(__name__)
logger = logging.getLogger('RAWPOWER')
logger.setLevel(logging.INFO)
# Create a File Handler
#filemode='w' == Truncate file to zero length or create text file for writing.
#The stream is positioned at the beginning of the file.
#handler = logging.FileHandler('/home/pi/steca/rawpower.log', mode='w')
handler = logging.FileHandler(MYDICT["rawlog"], mode='w')
handler.setLevel(logging.INFO)
# End Define Logging -> use logger.info('')
handler = TimedRotatingFileHandler(MYDICT["rawlog"],
                                   when='midnight',
                                   backupCount=3)
#handler = TimedRotatingFileHandler(MYDICT["rawlog"],
#                                   when='midnigth',
#                                   interval=1,
#                                   backupCount=3)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
#-----------------------------------------------------------------------------

#  Tämä formaattin toimii
#print(f'Teho on: {MYDICT["teho"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')
#logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')

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
def set_var_init_access_time():
    ''''
    Set initial timestamp for variables.json file
    '''
    MYDICT["ctimeinit"] = round(os.stat(MYDICT["varfile"]).st_ctime)
def check_var_access_time():
    ''''
    Reload variables.json parameters if file ctime has been changed
    '''
    MYDICT["ctime"] = round(os.stat(MYDICT["varfile"]).st_ctime)
    if MYDICT["ctimeinit"] == MYDICT["ctime"]:
        #print("Ei muutoksia variables.json tiedostoon...")
        return True
    else:
        MYDICT["ctimeinit"] = MYDICT["ctime"]
        reload_vars()
        #print(f'Teho on: {MYDICT["power"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')
        #print(MYDICT["ctime"])
        logger.info(f'Uudet arvot Teho on: {MYDICT["power"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')
def reload_vars():
    ''''
    Reload power, start and stoptimes from variables.json file
    '''
    with open(MYDICT["varfile"]) as f:
        variables = json.load(f)
    MYDICT["power"] = int(variables['power'])
    MYDICT["start"] = int(variables['start'])
    MYDICT["stop"] = int(variables['stop'])
def starttime():
    '''
    Calculation of starttime
    '''
    MYDICT['starttime'] = int(time.time_ns())
    #logger.info(f'Starttime aloitusaika: {MYDICT["starttime"]}')
def endtime():
    '''
    Calculation of endtime
    '''
    MYDICT['endtime'] = int(time.time_ns())
    #logger.info(f'Endtime lopetusaika: {MYDICT["endtime"]}')
def calctime():
    '''
    Calculation of time from start and endtime
    '''
    timediff = int(MYDICT['endtime']) - int(MYDICT['starttime'])
    MYDICT['timediff'] = int(timediff / 1000000000)
    MYDICT['total'] = int(MYDICT['timediff']) + int(MYDICT['total'])
    mins, secs = divmod(MYDICT['total'], 60)
    hours, mins = divmod(mins, 60)
    #print("{}, {}".format(MYDICT['timediff'], MYDICT['total']))
    logger.info(f'Vastus ollut päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')
def calctotaltimeon():
    '''
    Calculates how long Vastus has been on
    '''
    mins, secs = divmod(MYDICT['total'], 60)
    hours, mins = divmod(mins, 60)
    # Zero daily total time
    MYDICT['total'] = int(0)
    #print(f'Total Time On Today: {hours:d}:{mins:02d}:{secs:02d}')
    #print("Total Time on today: {}:{}:{}".format(hours, mins, secs))
    logger.info(f'Kokonaisaika päällä tänään: {hours:d}:{mins:02d}:{secs:02d}')
def logger_on():
    ''''
    Logger info when water heating is ON
    '''
    logger.info('Vastus päällä')
def logger_off_night():
    ''''
    Logger info when outside active hours
    '''
    #logger.info('Yöaika')
def logger_off():
    ''''
    Logger info when water heating is OFF
    '''
    logger.info('Vastus pois päältä')
def read_ac_power(data):
    ''''
    https://stackoverflow.com/questions/59802202/python-3-xml-data-to-variables
    '''
    variable=soup(data,'lxml')
    val=variable.findAll('measurement')[6]
    if val.get('value') == None:
        return 0
    else:
        return val['value']
def hae_teho():
    ''''
    Fetch XML-data from Steca inverter and change String-to-Float using read_ac_power-function
    '''
    try:
        r = requests.get(MYDICT["url"],timeout=5)
        r.raise_for_status()
        MYDICT['teho'] = round(float(read_ac_power(r.text)))
        logger.info(f'Teho nyt: {MYDICT["teho"]} Counter1: {MYDICT["counter1"]}')
        # Store Steca power number to a file to be used by flask-web-interface
        my_data = {
            "teho": MYDICT["teho"],
            }
        with open(MYDICT['varfile1'], 'w') as f:
            json.dump(my_data, f, indent=4)
            f.close()
    except requests.exceptions.RequestException as err:
        #print ("Whaat: Something Else",err)
        logger.info(f'Whaat: Something Else {err}')
        MYDICT['teho'] = int(0)
    except requests.exceptions.HTTPError as errh:
        #print ("Http Error:",errh)
        logger.info(f'Http Error: {errh}')
        MYDICT['teho'] = int(0)
    except requests.exceptions.ConnectionError as errc:
        #print ("Error Connecting:",errc)
        logger.info(f'Error Connecting: {errc}')
        MYDICT['teho'] = int(0)
    except requests.exceptions.Timeout as errt:
        #print ("Timeout Error:",errt)
        logger.info(f'Timeout Error: {errt}')
        MYDICT['teho'] = int(0)
def add_counter1():
    '''
    Add counter 1
    '''
    MYDICT['counter1'] = MYDICT['counter1'] + 1
def add_counter2():
    '''
    Add counter 2
    '''
    MYDICT['counter2'] = MYDICT['counter2'] + 1
def add_counter3():
    '''
    Add counter 3
    '''
    MYDICT['counter3'] = MYDICT['counter3'] + 1
def add_counter4():
    '''
    Add counter 4
    '''
    MYDICT['counter4'] = MYDICT['counter4'] + 1
def add_counter5():
    '''
    Add counter 5
    '''
    MYDICT['counter5'] = MYDICT['counter5'] + 1
def checkonTime():
    '''
    Check if time is between stop and start parameters
    '''
    date_time = datetime.datetime.now()
    date = date_time.date()
    aika = date_time.time()
    MYDICT['tunti'] = int(aika.hour)
    #print(MYDICT['tunti'])
    if MYDICT['tunti'] >= MYDICT['start'] and MYDICT['tunti'] <= MYDICT['stop']:
        MYDICT['onTime'] = True
    else:
        MYDICT['onTime'] = False
def checkonoff():
    '''
    Check if there is enough power to turn on solar heating
    '''
    if MYDICT['teho'] >= MYDICT['power']:
        MYDICT['onoff'] = True
    else:
        MYDICT['onoff'] = False

hae_teho()
checkonTime()
checkonoff()
set_var_init_access_time()
check_var_access_time()
logger.info(f'Alustusarvot -  Teho on: {MYDICT["power"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')

try:
  while (True):
    while MYDICT['onTime']:
      if MYDICT['onTime'] and MYDICT['onoff']:
        while MYDICT['counter1'] < 5 and MYDICT['onoff']:
          time.sleep(10)
          add_counter1()
          hae_teho()
          checkonoff()
          #print(MYDICT['onoff'])
        while  MYDICT['onTime'] and MYDICT['onoff']:
          MYDICT['counter3'] = 0
          MYDICT['counter4'] = 0
          MYDICT['counter5'] = 0
          GPIO.output(Rele1,GPIO.LOW) #Rele on päällä
          if MYDICT['counter1'] == 5:
              starttime()
              add_counter1()
          logger_on()
          add_counter2()
          time.sleep(60)
          check_var_access_time()
          hae_teho()
          checkonoff()
          checkonTime()
      if MYDICT['onTime'] and not MYDICT['onoff']:
        while MYDICT['counter3'] < 5 and not MYDICT['onoff']:
          time.sleep(60)
          add_counter3()
          hae_teho()
          checkonoff()
        while MYDICT['onTime'] and not MYDICT['onoff']:
          MYDICT['counter1'] = 0
          MYDICT['counter2'] = 0
          GPIO.output(Rele1,GPIO.HIGH) #Rele pois päältä
          if MYDICT['counter3'] == 5 and  MYDICT['starttime'] > 0:
              endtime()
              calctime()
              add_counter3()
          add_counter4()
          logger_off()
          time.sleep(60)
          check_var_access_time()
          hae_teho()
          checkonoff()
          checkonTime()
    while not MYDICT['onTime']:
      logger_off_night()
      if MYDICT['counter5'] == 0 and MYDICT['onoff']:
          endtime()
          calctime()
      if MYDICT['counter5'] == 0 and MYDICT['starttime'] > 0:
          calctotaltimeon() 
          send_email()
          add_counter5()
      time.sleep(300)
      checkonTime()
      hae_teho()
      checkonoff()
      check_var_access_time()
      GPIO.output(Rele1,GPIO.HIGH) #Rele pois päältä
finally:
  print ("Cleaning up")
  GPIO.cleanup()
