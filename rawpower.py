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
# Alustaa Releet
GPIO.setup(Rele1,GPIO.OUT)
GPIO.setup(Rele2,GPIO.OUT)
GPIO.setup(Rele3,GPIO.OUT)
GPIO.output(Rele1,GPIO.HIGH) #Vastus off
GPIO.output(Rele2,GPIO.HIGH) #Vastus off
GPIO.output(Rele3,GPIO.HIGH) #Vastus off

# Ladataan muuttujat tiedostosta
#with open('/home/pi/steca/variables.json') as f:
#    variables = json.load(f)

MYDICT = {
    "starttime": int(0),
    "endtime": int(0),
    "timediff": int(0),
    "total": int(0),
    "totalday": int(0),
    "onTime": '',
    "offTime": '',
    "onoff": '',
    "onoff0": '',
    "onoff1": '',
    "onoff2": '',
    "onoff3": '',
    "onoff4": '',
    "onoff5": '',
    "url": 'http://192.168.8.132/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData',
    "email": "ai@iki.fi",
    "tunti": '',
    "counter1": '',
    "counter2": '',
    "counter3": '',
    "counter4": '',
    "counter5": '',
    "counter6": '',
    "ctimeinit": '',
    "ctime": '',
    "rawlog": '/home/pi/steca/rawpower.log',
    "varfile": '/home/pi/steca/variables.json',
    "varfile1": '/home/pi/steca/power.json',
    "power": '',
    "power1": '',
    "power2": '',
    "power3": '',
    "teho": '' ,
    "power": '',
    "start": '',
    "stop": ''
}

with open(MYDICT["varfile"]) as f:
    variables = json.load(f)

MYDICT["power"] = int(variables["power"])
MYDICT["power1"] = int(variables["power1"])
MYDICT["power2"] = int(variables["power2"])
MYDICT["power3"] = int(variables["power3"])
MYDICT["start"] = int(variables["start"])
MYDICT["stop"] = int(variables["stop"])
MYDICT['counter1'] = int(0)
MYDICT['counter2'] = int(0)
MYDICT['counter3'] = int(0)
MYDICT['counter4'] = int(0)
MYDICT['counter4'] = int(0)
MYDICT['counter5'] = int(0)
MYDICT['counter6'] = int(0)

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
    # Send the message via Telia's SMTP server.
    s = smtplib.SMTP('mail.inet.fi')
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
        logger.info(f'Uudet arvot Teho1: {MYDICT["power"]}'
                                          f' Teho2: {MYDICT["power1"]}'
                                          f' Teho3: {MYDICT["power2"]}'
                                          f' Teho4: {MYDICT["power3"]}'
                                          f' Start: {MYDICT["start"]}'
                                          f' Stop: {MYDICT["stop"]}')
def reload_vars():
    ''''
    Reload power, start and stoptimes from variables.json file
    '''
    with open(MYDICT["varfile"]) as f:
        variables = json.load(f)
    MYDICT["power"] = int(variables['power'])
    MYDICT["power1"] = int(variables['power1'])
    MYDICT["power2"] = int(variables['power2'])
    MYDICT["power3"] = int(variables['power3'])
    MYDICT["start"] = int(variables['start'])
    MYDICT["stop"] = int(variables['stop'])
def totaldaytozero():
    '''
    Zero Total Time per Day after operating hours
    '''
    MYDICT['totalday'] = int(0)
    #logger.info(f'Starttime aloitusaika: {MYDICT["starttime"]}')
def totaldayon():
    '''
    Calculate Total Time per Day ON
    '''
    MYDICT['totalday'] = MYDICT['totalday'] + 1
    #logger.info(f'Today ON: {MYDICT["totalday"]} minutes')
    logger.info(f'Today ON: {MYDICT["totalday"]} min, {MYDICT["teho"]}W')
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
    #logger.info('Vastus päällä')
    logger.info(f'Vastus päällä, {MYDICT["totalday"]} minutes')
def logger_off_night():
    ''''
    Logger info when outside active hours
    '''
    logger.info('Yöaika')
def logger_off():
    ''''
    Logger info when water heating is OFF
    '''
    logger.info('Rele1&2&3 OFF, No POWER')
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
        if not 'PAC' in r.text:
            MYDICT['teho'] = int(0)
        else:
            jsondata = r.json()
            MYDICT['teho'] = jsondata['Body']['Data']['PAC']['Value']
            #MYDICT['teho'] = round(float(read_ac_power(r.text)))
            #logger.info(f'Teho nyt: {MYDICT["teho"]} Counter1: {MYDICT["counter1"]}')
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
def add_counter6():
    '''
    Add counter 6
    '''
    MYDICT['counter6'] = MYDICT['counter6'] + 1
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
#def checkonoff():
#    '''
#    Check if there is enough power to turn on solar heating
#    '''
#    if MYDICT['teho'] >= MYDICT['power']:
#        MYDICT['onoff'] = True
#    else:
#        MYDICT['onoff'] = False
def checkonoff():
    '''
    Check if there is enough power to turn on solar heating
    '''
    if MYDICT['teho'] >= MYDICT['power'] and MYDICT['teho'] < MYDICT['power1']:
        # Teho valilla 500-750
        # Rele 1 vetaa, Rele2 ei veda, Rele3 ei veda
        MYDICT['onoff1'] = True
        MYDICT['onoff0'] = False
        MYDICT['onoff2'] = False
        MYDICT['onoff3'] = False
        MYDICT['onoff4'] = False
    elif MYDICT['teho'] >= MYDICT['power1'] and MYDICT['teho'] < MYDICT['power2']:
        # Teho valilla 750-1200
        # Rele 1 ei veda, Rele2 vetaa, Rele3 ei veda
        MYDICT['onoff2'] = True
        MYDICT['onoff0'] = False
        MYDICT['onoff1'] = False
        MYDICT['onoff3'] = False
        MYDICT['onoff4'] = False
    elif MYDICT['teho'] >= MYDICT['power2'] and MYDICT['teho'] < MYDICT['power3']:
        # Teho valilla 1200-1500
        # Rele 1 vetaa, Rele2 vetaa, Rele3 ei veda
        MYDICT['onoff3'] = True
        MYDICT['onoff0'] = False
        MYDICT['onoff1'] = False
        MYDICT['onoff2'] = False
        MYDICT['onoff4'] = False
    elif MYDICT['teho'] >= MYDICT['power3']:
        # Teho yli 1500
        # Rele 1 ei veda, Rele2 vetaa, Rele3 vetaa
        MYDICT['onoff4'] = True
        MYDICT['onoff0'] = False
        MYDICT['onoff1'] = False
        MYDICT['onoff2'] = False
        MYDICT['onoff3'] = False
    else:
        MYDICT['onoff0'] = True
        MYDICT['onoff1'] = False
        MYDICT['onoff2'] = False
        MYDICT['onoff3'] = False
        MYDICT['onoff4'] = False
def coming_up():
    #logger.info(f'Coming UP {MYDICT["teho"]}W > {MYDICT["power"]}W, Count to 5: {MYDICT["counter1"]}')
    time.sleep(30)
    basic_checks()
def is_up():
    time.sleep(60)
    totaldayon()
    basic_checks()
def no_power():
    logger_off()
    time.sleep(60)
    basic_checks()
    #logger.info(f'Rele1&2&3 is OFF: counter {MYDICT["counter5"]}, {MYDICT["teho"]}')
#def counters_to_zero(d1):
#    MYDICT['counter{d1}'] = 0
#    #print(f"MYDICT['counter{d1}'] on {MYDICT['counter{d1}']}")
def is_offhours():
    #logger.info('Is OFF')
    logger_off_night()
    time.sleep(300)
    basic_checks()
def basic_checks():
    hae_teho()
    checkonoff()
    checkonTime()
    check_var_access_time()

hae_teho()
checkonTime()
checkonoff()
set_var_init_access_time()
check_var_access_time()
#logger.info(f'Alustusarvot -  Teho on: {MYDICT["power"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')
logger.info(f'Uudet arvot Teho1: {MYDICT["power"]}'
                                  f' Teho2: {MYDICT["power1"]}'
                                  f' Teho3: {MYDICT["power2"]}'
                                  f' Teho4: {MYDICT["power3"]}'
                                  f' Start: {MYDICT["start"]}'
                                  f' Stop: {MYDICT["stop"]}')
try:
  while (True):
    while MYDICT['onTime']:
      if MYDICT['onTime'] and MYDICT['onoff1']:
        while MYDICT['counter1'] < 5 and MYDICT['onoff1']:
          #print(f'onoff1 counter {MYDICT["counter1"]}')
          logger.info(f'Rele1 coming up in 5: {MYDICT["counter1"]}, {MYDICT["teho"]}W')
          coming_up()
          add_counter1()
        while MYDICT['onTime'] and MYDICT['onoff1']:
          GPIO.output(Rele1,GPIO.LOW) #Rele1 on paalla, 670W
          GPIO.output(Rele2,GPIO.HIGH) #Rele1 on paalla, 670W
          GPIO.output(Rele3,GPIO.HIGH) #Rele1 on paalla, 670W
          #print("Rele1 ON, Rele2&3 OFF")
          if MYDICT['counter1'] == 5:
              add_counter1()
              logger.info('Rele1 ON, Rele2&3 OFF')
              MYDICT['counter0'] = int(0)
              MYDICT['counter2'] = int(0)
              MYDICT['counter3'] = int(0)
              MYDICT['counter4'] = int(0)
              MYDICT['counter5'] = int(0)
              MYDICT['counter6'] = int(0)
          is_up()
      if MYDICT['onTime'] and MYDICT['onoff2']:
        while MYDICT['counter2'] < 5 and MYDICT['onoff2']:
          #print(f'onoff2 counter {MYDICT["counter2"]}')
          logger.info(f'Rele2 coming up in 5: {MYDICT["counter2"]}, {MYDICT["teho"]}W')
          coming_up()
          add_counter2()
        while  MYDICT['onTime'] and MYDICT['onoff2']:
          #for i in [1, 3, 4, 5]:
          #    counters_to_zero(i)
          GPIO.output(Rele2,GPIO.LOW) #Rele2 on paalla, 1500W
          GPIO.output(Rele1,GPIO.HIGH) #Rele1 pois paalta, 1500W
          GPIO.output(Rele3,GPIO.HIGH) #Rele1 pois paalta, 1500W
          #print("Rele2 ON, Rele1&3 OFF ")
          if MYDICT['counter2'] == 5:
              add_counter2()
              logger.info('Rele2 ON, Rele1&3 OFF')
              MYDICT['counter0'] = int(0)
              MYDICT['counter1'] = int(0)
              MYDICT['counter3'] = int(0)
              MYDICT['counter4'] = int(0)
              MYDICT['counter5'] = int(0)
              MYDICT['counter6'] = int(0)
          is_up()
      if MYDICT['onTime'] and MYDICT['onoff3']:
        while MYDICT['counter3'] < 5 and MYDICT['onoff3']:
          #print(f'onoff3 counter {MYDICT["counter3"]}')
          logger.info(f'Rele1&2coming up in 5: {MYDICT["counter3"]}, {MYDICT["teho"]}W')
          coming_up()
          add_counter3()
        while  MYDICT['onTime'] and MYDICT['onoff3']:
          GPIO.output(Rele1,GPIO.LOW) #Rele1 ON, 2300W
          GPIO.output(Rele2,GPIO.LOW) #Rele2 ON, 2300W
          GPIO.output(Rele3,GPIO.HIGH) #Rele3 OFF, 2300W
          if MYDICT['counter3'] == 5:
              add_counter3()
              logger.info('Rele1&2 ON, Rele3 OFF')
              MYDICT['counter0'] = int(0)
              MYDICT['counter1'] = int(0)
              MYDICT['counter2'] = int(0)
              MYDICT['counter4'] = int(0)
              MYDICT['counter5'] = int(0)
              MYDICT['counter6'] = int(0)
          is_up()
      if MYDICT['onTime'] and MYDICT['onoff4']:
        while MYDICT['counter4'] < 5 and MYDICT['onoff4']:
          #print(f'onoff4 counter {MYDICT["counter4"]}')
          logger.info(f'Rele2&3 coming up in 5: {MYDICT["counter4"]}, {MYDICT["teho"]}W')
          coming_up()
          add_counter4()
        while  MYDICT['onTime'] and MYDICT['onoff4']:
          GPIO.output(Rele1,GPIO.HIGH) #Rele1 pois paalta, 670W
          GPIO.output(Rele2,GPIO.LOW) #Rele2 on paalla, 670W
          GPIO.output(Rele3,GPIO.LOW) #Rele3 on paalla, 670W
          if MYDICT['counter4'] == 5:
              add_counter4()
              logger.info('Rele2&3 ON, Rele1 OFF')
              MYDICT['counter0'] = int(0)
              MYDICT['counter1'] = int(0)
              MYDICT['counter2'] = int(0)
              MYDICT['counter3'] = int(0)
              MYDICT['counter5'] = int(0)
              MYDICT['counter6'] = int(0)
          is_up()
      if MYDICT['onTime'] and MYDICT['onoff0']:
        while MYDICT['counter5'] < 5 and MYDICT['onoff0']:
          #print(f'onoff0 counter {MYDICT["counter5"]}')
          logger.info(f'Rele1&2&3 going down (No POWER)in 5: {MYDICT["counter5"]}, {MYDICT["teho"]}W > {MYDICT["power"]}W')
          coming_up()
          add_counter5()
        while MYDICT['onTime'] and MYDICT['onoff0']:
          GPIO.output(Rele1,GPIO.HIGH) #Rele pois päältä
          GPIO.output(Rele2,GPIO.HIGH) #Rele pois päältä
          GPIO.output(Rele3,GPIO.HIGH) #Rele pois päältä
          if MYDICT['counter5'] == 5 and  MYDICT['totalday'] > 0:
              add_counter5()
              logger.info('Rele1&2&3 OFF')
              MYDICT['counter0'] = int(0)
              MYDICT['counter1'] = int(0)
              MYDICT['counter2'] = int(0)
              MYDICT['counter3'] = int(0)
              MYDICT['counter4'] = int(0)
              MYDICT['counter6'] = int(0)
          add_counter5()
          no_power()
    while not MYDICT['onTime']:
      #logger_off_night()
      #if MYDICT['counter5'] == 0 and MYDICT['onoff']:
          #endtime()
          #calctime()
      if MYDICT['counter6'] == 0 and MYDICT['totalday'] > 0:
          #calctotaltimeon()
          MYDICT['counter0'] = int(0)
          MYDICT['counter1'] = int(0)
          MYDICT['counter2'] = int(0)
          MYDICT['counter3'] = int(0)
          MYDICT['counter4'] = int(0)
          MYDICT['counter5'] = int(0)
          totaldaytozero()
          send_email()
          add_counter6()
      GPIO.output(Rele1,GPIO.HIGH) #Rele pois päältä
      is_offhours()
finally:
  print ("Cleaning up")
  GPIO.cleanup()
