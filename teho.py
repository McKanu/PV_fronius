import requests
import logging
from bs4 import BeautifulSoup as soup
import requests
import lxml

#MYDICT = {
#    "teho": ""
#}


def read_ac_power(data):
    ''''
    https://stackoverflow.com/questions/59802202/python-3-xml-data-to-variables
    '''
    variable=soup(data,'lxml')
    val=variable.findAll('measurement')[6]
    return val['value']

class hae_teho_steca():
    ''''
    Fetch XML-data from Steca inverter and change String-to-Float using read_ac_power-function
    '''
    r = requests.get('http://192.168.10.59/measurements.xml')
    #MYDICT['teho'] = round(float(read_ac_power(r.text)))
    teho = round(float(read_ac_power(r.text)))
    logger.info(f'Teho nyt: {MYDICT["teho"]} Counter1: {MYDICT["counter1"]}')
    return teho

class hae_teho_fronius():
    ''''
    Fetch JSON-data from Fronius inverter and change String-to-Float using read_ac_power-function
    '''
    r = requests.get('http://192.168.10.59/measurements.xml')
    MYDICT['teho'] = round(float(read_ac_power(r.text)))
    logger.info(f'Teho nyt: {MYDICT["teho"]} Counter1: {MYDICT["counter1"]}')
