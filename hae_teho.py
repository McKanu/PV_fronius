import requests
import json
# Urli vaihdettu 4.7.2020 192.168.8.104 -> 192.168.8.132
MYDICT = {
#    "url": 'http://192.168.8.104/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData',
    "url": 'http://192.168.8.132/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData',
    "teho": int(0)
}

r = requests.get(MYDICT["url"],timeout=5)
if not 'PAC' in r.text:
    MYDICT['teho'] = int(0)
    print("PAC Key wasn't found in json.data from Fronius")
else:
    jsondata = r.json()
    MYDICT['teho'] = jsondata['Body']['Data']['PAC']['Value']

print(MYDICT['teho'])
