#!/usr/bin/python

import json
# Lib from https://github.com/adafruit/Adafruit_Python_DHT
import Adafruit_DHT

# Configuration
sensor = Adafruit_DHT.DHT11
platform = Adafruit_DHT
pin = 23
backupFile = "DHT11.json"

# Read sensor
humidity, temperature = Adafruit_DHT.read(sensor, pin)
live = True

# Fallback to last value on error
if humidity is None or temperature is None:
	file = open(backupFile, "r")
	data = json.load(file)
	file.close()
	humidity = data['humidity']
	temperature = data['temperature']
	live = False

# Display
print 'Temperature: {0:.1f} *C - Humidity: {1:.1f} % - Live: {2}'.format(temperature, humidity, live)

# Save for future error(s)
if live:
	file = open(backupFile, "w")
	data = {'temperature': temperature, 'humidity': humidity}
	json.dump(data, file)
	file.close()
