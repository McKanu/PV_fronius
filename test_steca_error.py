import RPi.GPIO as GPIO
import time
import datetime
import os
import subprocess
import json
from bs4 import BeautifulSoup as soup
import lxml
import requests
import logging

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
    "varfile1": '/home/pi/steca/power.json',
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
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
# End Define Logging -> use logger.info('')


#  Tämä formaattin toimii
#print(f'Teho on: {MYDICT["teho"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')
def hae_teho():
    #r = requests.get('http://192.168.10.59/measurements.xml')
    #url='http://192.168.10.59/measurements.xml'
    url='http://192.168.10.59/measurementss.xml'
    try:
        r = requests.get(url,timeout=3)
        r.raise_for_status()
        MYDICT['teho'] = round(float(read_ac_power(r.text)))
        logger.info(f'Teho nyt: {MYDICT["teho"]} Counter1: {MYDICT["counter1"]}')
        my_data = {
            "teho": MYDICT["teho"],
            }
        with open(MYDICT['varfile1'], 'w') as f:
            json.dump(my_data, f, indent=4)
            f.close()
        #print(data.findAll('measurement')[6])
        #data = soup(r.text, 'lxml')
        #print(data)
        #values=data.findAll('measurement')[6]
        #print(values)
        #print(val['value'])
        #print(values['value'])
    except requests.exceptions.RequestException as err:
        print ("Whaat: Something Else",err)
        logger.info(f'Whaat: Something Else {err}')
        MYDICT['teho'] = int(0)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        logger.info(f'Http Error: {errh}')
        MYDICT['teho'] = int(0)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        logger.info(f'Error Connecting: {errc}')
        MYDICT['teho'] = int(0)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)     
        logger.info(f'Timeout Error: {errt}')
        MYDICT['teho'] = int(0)
    #for i in range (0, len(data.findAll('measurement'))):
    #    print(data.findAll('measurement')[i])
    #print(data.findAll('measurement')[6])
    #data = soup(r.text, 'lxml')
    #print(data)
    #values=data.findAll('measurement')[6]
    #print(values)
    #print(val['value'])
    #print(values['value'])
def read_ac_power(data):
    ''''
    https://stackoverflow.com/questions/59802202/python-3-xml-data-to-variables
    '''
    variable=soup(data,'lxml')
    val=variable.findAll('measurement')[6]
    print(val)
    #print(type(val))
    #print(val['value'])
    #print(type(val['value']))
    if val.get('value') == None:
        print("Ei Löydy")
        return 0
    else:
        print("Löytyy")
        return val['value']
#    if 'value' in val:
#        print("Value löytyy")
#        return val['value']
#    else:
#        print("Value ei löydy")
#        return 0
def hae_tehoo():
    ''''
    Fetch XML-data from Steca inverter and change String-to-Float using read_ac_power-function
    '''
    r = requests.get('http://192.168.10.59/measurements.xml')
    MYDICT['teho'] = round(float(read_ac_power(r.text)))
    print(f'Teho nyt: {MYDICT["teho"]}')
    logger.info(f'Teho nyt: {MYDICT["teho"]} Counter1: {MYDICT["counter1"]}')
    my_data = {
        "teho": MYDICT["teho"],
        }
    with open(MYDICT['varfile1'], 'w') as f:
        json.dump(my_data, f, indent=4)
        f.close()
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

for i in range(0, 10):
    starttime()
    hae_teho()
    time.sleep(7)
    endtime()
    calctime()
calctotaltimeon()
