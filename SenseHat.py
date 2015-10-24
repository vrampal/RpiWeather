#!/usr/bin/python
import time
import json

DATA_FILE = "SenseHat.json"
CACHE_ALIVE = 5 # seconds
PRESSURE_OFFSET = 24.5 # = 206 m altitude

class SenseHat2(object):

	def __init__(self):
		self.data       = None
		self.humidity   = None
		self.tempH      = None
		self.pressure   = None
		self.tempP      = None
		self.mesureTime = 0

	def loadDataFile(self):
		try:
			file = open(DATA_FILE, "r")
			self.data = json.load(file)
			file.close()
			self.humidity    = self.data['humidity']
			self.tempH       = self.data['tempH']
			self.pressure    = self.data['pressure']
			self.tempP       = self.data['tempP']
			self.mesureTime  = self.data['mesureTime']
		except Error:
			print 'Error loading data file'
		
	def saveDataFile(self):
		try:
			file = open(DATA_FILE, "w")
			self.data = {'mesureTime': self.startTime, 'humidity': self.humidity, 'tempH': self.tempH, 'pressure': self.pressure, 'tempP': self.tempP}
			json.dump(self.data, file)
			file.close()
		except IOError:
			print 'Error saving data file'

	def readSensor(self):
		from sense_hat import SenseHat
		senseHat = SenseHat()
		self.humidity   = senseHat.get_humidity()
		self.tempH      = senseHat.get_temperature_from_humidity()
		self.pressure   = senseHat.get_pressure() + PRESSURE_OFFSET
		self.tempP      = senseHat.get_temperature_from_pressure()
		self.mesureTime = time.time()

	def main(self):
		self.loadDataFile()
		if (time.time() > (self.mesureTime + CACHE_ALIVE)):
			try:
				self.readSensor()
				self.saveDataFile()
			except:
				print 'Error reading sensor'
				self.humidity    = self.data['humidity']
				self.tempH       = self.data['tempH']
				self.pressure    = self.data['pressure']
				self.tempP       = self.data['tempP']
		print 'TempH: {0:.2f} *C - Humidity: {1:.2f} %'.format(self.tempH, self.humidity)
		print 'TempP: {0:.2f} *C - Pressure: {1:.2f} mbar'.format(self.tempP, self.pressure)

if __name__ == '__main__':
	SenseHat2().main()

