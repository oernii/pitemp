#!/usr/bin/python
import sys
import Adafruit_DHT
import requests
import time

sensor=Adafruit_DHT.AM2302
pin="23"

sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

if humidity is not None and temperature is not None:
	host="rtemp1"
	data="temp_humidity,host={0:s} temp={1:0.1f},humidity={2:0.1f} {3:0.0f}000000004".format(host, temperature, humidity, time.time())
	r = requests.post('http://192.168.1.100:8086/write?db=temp', data )
else:
    print('Failed to get reading. Try again!')
    sys.exit(1)
