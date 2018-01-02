#!/usr/bin/python
import sys
import os
import Adafruit_DHT
import requests
import time
import six

if six.PY2:
    import ConfigParser as configparser
else:
    import configparser

configParser = configparser.RawConfigParser()   
configFilePath = os.path.expanduser('~/.pitemp.cfg')
configParser.read(configFilePath)

pin  = configParser.get('pitemp', 'pin')
host = configParser.get('pitemp', 'host')
url  = configParser.get('pitemp', 'url')
sensor = int(configParser.get('pitemp', 'sensor'))

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries=3, delay_seconds=0)

if humidity is not None and temperature is not None:
  data="temp_humidity,host={0:s} temp={1:0.1f},humidity={2:0.1f} {3:0.0f}000000004".format(host, temperature, humidity, time.time())
  #print data
  #print url
  r = requests.post(url + 'write?db=temp', data )
else:
  print('Failed to get reading. Try again!')
  sys.exit(1)
