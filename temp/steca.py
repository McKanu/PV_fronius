import urllib.request
import urllib.parse
import xml.etree.cElementTree as ET  # or with try/except as per your edit
import re


try:
    req = urllib.request.Request('http://91.153.139.251:8888/measurements.xml')
    resp = urllib.request.urlopen(req)
    respData = resp.read()

    saveFile = open('steca.txt','w')
    saveFile.write(str(respData))
    saveFile.close()

    with open('steca.txt','r') as file:
        #data=file.read()
        data=file.read().replace('<M','\n<M')
        data=re.sub(r"^./*Value=","",str(data))
    print (data)

    #read_file = open("steca.txt","r")
    #print (open(data_file,'r'))
    #print (data)
    #data_file = data
    #xmlD = ET.fromstring(data_file)
    #xmlD = ET.parse(data_file)
    #root = xmlD.getroot()
    '''
    xml_dict = {}
    # first get the key & val for 'cbt'
    Value_val = tree.find('Type').find('Value').text
    xml_dict['Value'] = Value_val
    #print (xml_dict)


    tree = ET.parse(open(r'c:\GIT-repos\Python\steca.txt','r'))
    #print (respData)
    # <?xml version='1.0' encoding='UTF-8'?>
    #tree = ET.parse(open('steca.txt','r')

    #xml_data1 = """<?xml version='1.0' encoding='UTF-8'?>"""
    #xml_data1 = open(str('steca.txt','r')
    #tree = ET.fromstring(xml_data1)  # or `ET.parse(<filename>)`
    #tree = ET.ElementTree(file='steca.txt')
    xml_dict = {}
    # first get the key & val for 'cbt'
    Value_val = tree.find('Value').find('Type').text
    xml_dict['Value'] = Value_val
    print (xml_dict)
    '''

except Exception as e:
    print (str(e))