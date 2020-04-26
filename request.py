from bs4 import BeautifulSoup as soup
import requests
import lxml
import json

with open('/home/pi/steca/variables.json') as f:
    variables = json.load(f)

MYDICT = {
    "counter1": '',
    "counter2": '',
    "counter3": '',
    "counter4": '',
    "counter5": '',
    "power": "",
    "teho": "",
    "power": variables['power'],
    "start": variables['start'],
    "stop": variables['stop']
}

def read_ac_power(data):
    variable=soup(data,'lxml')
    val=variable.findAll('measurement')[6]
    return val['value']

def hae_teho():
    r = requests.get('http://192.168.10.59/measurements.xml')
    MYDICT['teho'] = round(float(read_ac_power(r.text)))
    print(MYDICT['teho'])
    print(MYDICT['power'])

hae_teho()

