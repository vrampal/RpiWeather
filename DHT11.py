#!/usr/bin/python
import time
import json
# Requires lib from https://github.com/adafruit/Adafruit_Python_DHT

DATA_FILE   = "DHT11.json"
CACHE_ALIVE = 5 # seconds
SENSOR_PIN  = 23

class DHT11(object):

	def __init__(self):
		self.data        = None
		self.humidity    = None
		self.temperature = None
		self.mesureTime  = 0

	def loadDataFile(self):
		try:
			file = open(DATA_FILE, "r")
			self.data = json.load(file)
			file.close()
			self.humidity    = self.data['humidity']
			self.temperature = self.data['temperature']
			self.mesureTime  = self.data['mesureTime']
		except:
			print('Error loading data file')
		
	def saveDataFile(self):
		try:
			file = open(DATA_FILE, "w")
			self.data = {'mesureTime': self.mesureTime, 'humidity': self.humidity, 'temperature': self.temperature}
			json.dump(self.data, file)
			file.close()
		except IOError:
			print('Error saving data file')

	def readSensor(self):
		import Adafruit_DHT
		sensor = Adafruit_DHT.DHT11
		self.humidity, self.temperature = Adafruit_DHT.read(sensor, SENSOR_PIN)
		self.mesureTime = time.time()

	def main(self):
		self.loadDataFile()
		if (time.time() > (self.mesureTime + CACHE_ALIVE)):
			self.readSensor()
			if self.humidity is None or self.temperature is None:
				print('Error reading sensor')
				self.humidity    = self.data['humidity']
				self.temperature = self.data['temperature']
			else:
				self.saveDataFile()
		print('Temperature: {0:.1f} *C - Humidity: {1:.1f} %'.format(self.temperature, self.humidity))

if __name__ == '__main__':
	DHT11().main()
