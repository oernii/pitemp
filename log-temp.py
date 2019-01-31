#!/usr/bin/python
import sys
import os
import Adafruit_DHT
import requests
import time
import six
import shelve
import atexit
import argparse

if six.PY2:
    import ConfigParser as configparser
else:
    import configparser

# CONFIG
configParser = configparser.RawConfigParser()   
configFilePath = os.path.expanduser('~/.pitemp.cfg')
configParser.read(configFilePath)

pin  = configParser.get('pitemp', 'pin')
host = configParser.get('pitemp', 'host')
url  = configParser.get('pitemp', 'url')
sensor = int(configParser.get('pitemp', 'sensor'))

#argumenty
parser = argparse.ArgumentParser()
parser.add_argument('-o', action='store_true')
args = parser.parse_args()
offline =False

if args.o == True:
    offline = True

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


# COUNTER persistent
cou = shelve.open('/dev/shm/pitemp')
if not cou.has_key('errors'):
  cou['errors'] = 0

def savecounter():
    c = cou['errors']
    cou.close()
    if c > 30:
      os.system("/sbin/reboot")

atexit.register(savecounter)

# READ temp
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin, retries=3, delay_seconds=0)

# SUBMIT to influxdb
if humidity is not None and temperature is not None:
  data="temp_humidity,host={0:s} temp={1:0.1f},humidity={2:0.1f} {3:0.0f}000000004".format(host, temperature, humidity, time.time())

  if offline:
    print "curl -v -X POST " + url + 'write?db=temp' + ' -d \'' + data + '\''
  else:
    try:
      r = requests.post(url + 'write?db=temp', data )
      r.raise_for_status()
      cou['errors'] = 0
    except requests.exceptions.RequestException as e:  # This is the correct syntax
      cou['errors'] = cou['errors']+1
      print e
      print "Error counter: " + str(cou['errors'])
      sys.exit(1)
else:
  cou['errors'] = cou['errors']+1
  print('Failed to get reading. Try again!')
  print "Error counter: " + str(cou['errors'])
  sys.exit(1)
