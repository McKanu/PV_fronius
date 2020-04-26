import RPi.GPIO as GPIO
import time
import datetime
import subprocess
import json
import os

Rele1 = 26
Rele2 = 20
Rele3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Rele1,GPIO.OUT)
GPIO.output(Rele1,GPIO.HIGH) #Vastus ei ole päällä

MYDICT = {
    "counter1": '',
    "counter2": '',
    "counter3": '',
    "counter4": '',
    "counter5": '',
    "ctime": '',
    "ctimeinit": '',
    "filestatus": '',
    "varfile": '/home/pi/steca/variables.json',
    "power": "",
    "power": "",
    "start": "",
    "stop": "" 
}

with open(MYDICT["varfile"], 'r') as f:
    variables = json.load(f)

MYDICT["power"] = variables["power"]
MYDICT["start"] = variables["start"]
MYDICT["stop"] = variables["stop"]

#  Tämä formaattin toimii
print(f'Teho on: {MYDICT["power"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')

#varfile = 'variables.json'
MYDICT["ctimeinit"] = round(os.stat(MYDICT["varfile"]).st_ctime)
print(f'CTIME:{MYDICT["ctimeinit"]}')

def check_time():
    MYDICT["ctime"] = round(os.stat(MYDICT["varfile"]).st_ctime)
    if MYDICT["ctimeinit"] == MYDICT["ctime"]:
        #print("Ei muutoksia variables.json tiedostoon...")
        #continue
        #time.sleep(2)
        return True
    else:
        print("Variables.json tiedosto muuttunut....")
        MYDICT["ctimeinit"] = MYDICT["ctime"]
        reload_vars()
        print(f'Teho on: {MYDICT["power"]}, Start on: {MYDICT["start"]}, Stop on: {MYDICT["stop"]}')
        print(MYDICT["ctime"])
        time.sleep(5)

def reload_vars():
    with open(MYDICT["varfile"]) as f:
        variables = json.load(f)
    MYDICT["power"] = variables['power']
    MYDICT["start"] = variables['start']
    MYDICT["stop"] = variables['stop']

while True:
    check_time()
    time.sleep(1)
