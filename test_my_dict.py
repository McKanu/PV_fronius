import RPi.GPIO as GPIO
import time
import datetime
import os
import subprocess
import json
from teho import hae_teho_steca

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

def hae_teho():
    hae_teho_steca()
    print(f'Teho on: {MYDICT["teho"]}')
    
