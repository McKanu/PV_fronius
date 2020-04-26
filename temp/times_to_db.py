#!/usr/bin/env python3
'''
Calculate time difference and print it to log filr
'''
# encoding=utf-8
import datetime
#from datetime import datetime
import time
import logging
#import sys

#reload(sys)
#sys.setdefaultencoding('utf8')

#fmt = '%Y-%m-%d %H:%M:%S'
MYLIST = []
#__TIME0 = datetime.datetime.now().time().strftime('%H:%M:%S')
#__TIME1 = __TIME0
#__TOTAL_TIME = __TIME0

#MYLIST.append(TIME0)
#MYLIST.insert(0, TIME0)

#syslog.syslog("Starting up TIMES_TO_DB")
#logger = logging.getLogger(__name__)
LOGGER = logging.getLogger('TIMES_TO_DB')
LOGGER.setLevel(logging.INFO)
# Create a File Handler
#filemode='w'
HANDLER = logging.FileHandler('/home/pi/steca/rawpower.log', mode='w', encoding="utf-8")
HANDLER.setLevel(logging.INFO)
# create a logging format
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMATTER)
# add the handlers to the logger
LOGGER.addHandler(HANDLER)
# End Define Logging -> use logger.info('')


def add_time_start():
    '''
    Add start time to MYLIST[0]
    '''
    #global __TIME0
    # Add start time to index 0
    time0 = datetime.datetime.now().time().strftime('%H:%M:%S')
    MYLIST.insert(0, time0)

def calc_time():
    '''
    Add start time to MYLIST[1]
    '''
    #global __TIME1
    #global __TOTAL_TIME
    # Uusi aikaleima listaan indeksilla 1
    time1 = datetime.datetime.now().time().strftime('%H:%M:%S')
    MYLIST.insert(1, time1)
    #TOTAL_TIME=(datetime.datetime.strptime(TIME1,'%H:%M:%S')
    # - datetime.datetime.strptime(TIME0,'%H:%M:%S'))
    total_time = (datetime.datetime.strptime(MYLIST[1], '%H:%M:%S')\
        -datetime.datetime.strptime(MYLIST[0], '%H:%M:%S'))
    #syslog.syslog(syslog.LOG_INFO, "Vastus oli paalla %s" % TOTAL_TIME)
    LOGGER.info('Vastus oli paalla %s', total_time) # How long power was more than expected

add_time_start()

while True:
    time.sleep(5)
    calc_time()

#today = datetime.date.today()
#now = datetime.datetime.now()
#MYLIST.append(today)
#TIME1 = time.strftime("%Y-%m-%d %H:%M:%S")
#MYLIST.append(TIME1)
#time.sleep(10)
#time2 = time.strftime("%Y-%m-%d %H:%M:%S")
#MYLIST.append(time2)
#
#print (MYLIST[0]) # print the date object, not the container ;-)
#
## It's better to always use str() because :
#print ("This is a new day : ", MYLIST[0]) # will work
#print ("This is a new day : ", MYLIST[1]) # will work
##print ("This is a new day : ", MYLIST[2]) # will work
##print ("This is a new day : " + MYLIST[0]) # will crash)
#>>> cannot concatenate 'str' and 'datetime.date' objects
#
#print ("This is a new day : " + str(MYLIST[0]))
#print ("This is a new day : " + str(MYLIST[1]))
##print ("This is a new day : " + str(MYLIST[2]))
#diff = time2 - TIME1
#seconds = diff.seconds
#minutes = (diff.seconds)/60
#print (str(minutes) +' Minutes')

#import time
#start = time.time()
#MYLIST.append(start)
#time.sleep(10)  # or do something more productive
#done = time.time()
#MYLIST.append(done)
#elapsed = done - start
#print(elapsed)

#minutes = diff.minutes



#d1_ts = time.mktime(MYLIST[2].timetuple())
#d2_ts = time.mktime(MYLIST[2].timetuple())
#
#print (d1_ts + d2_ts)

#print (round(int(d2_ts-d1_ts) / 60))
