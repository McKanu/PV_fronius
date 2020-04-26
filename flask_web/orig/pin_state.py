from datetime import datetime
import json
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

MYDICT = {
    "varfile": '/home/pi/steca/variables.json',
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

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   26 : {'name' : 'Rele 1', 'state' : GPIO.LOW},
   20 : {'name' : 'Rele 2', 'state' : GPIO.LOW},
   21 : {'name' : 'Rele 3', 'state' : GPIO.LOW}
   }

# Setup each pins
#for pin in pins:
#   GPIO.setup(pin, GPIO.OUT)

def read_state():
    # Read current state for each pins
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        pins[pin]['state'] = GPIO.input(pin)
        print(pins[pin]['state'])

def reload_vars():
    ''''
    Reload power, start and stoptimes from variables.json file
    '''
    with open(MYDICT["varfile"]) as f:
        variables = json.load(f)
    MYDICT["power"] = int(variables['power'])
    MYDICT["start"] = int(variables['start'])
    MYDICT["stop"] = int(variables['stop'])

while True:
    read_state()
    time.sleep(6)
