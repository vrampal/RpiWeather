#!/usr/bin/python
import time
import json
from smbus import SMBus

DATA_FILE = "MS5611.json"
CACHE_ALIVE = 5 # seconds
BUS_SELECTION = 1
MS5611_ADDRESS = 0x77
PRESSURE_OFFSET = 24.5 # = 206 m altitude

class MS5611(object):

	def __init__(self):
		self.data        = None
		self.pressure    = None
		self.temperature = None
		self.mesureTime  = 0
		self.bus         = None

	def loadDataFile(self):
		try:
			file = open(DATA_FILE, "r")
			self.data = json.load(file)
			file.close()
			self.pressure    = self.data['pressure']
			self.temperature = self.data['temperature']
			self.mesureTime  = self.data['mesureTime']
		except:
			print 'Error loading data file'
		
	def saveDataFile(self):
		try:
			file = open(DATA_FILE, "w")
			self.data = {'mesureTime': self.mesureTime, 'pressure': self.pressure, 'temperature': self.temperature}
			json.dump(self.data, file)
			file.close()
		except IOError:
			print 'Error saving data file'

	def ms5611_read_block(self, command):
		data = self.bus.read_i2c_block_data(MS5611_ADDRESS, command)
		time.sleep(0.05)
		return data
		
	def ms5611_write_byte(self, data):
		self.bus.write_byte(MS5611_ADDRESS, data)
		time.sleep(0.05)

	def readSensor(self):
		# Bus init
		self.bus = SMBus(BUS_SELECTION)

		# Read calibration data
		C1 = self.ms5611_read_block(0xA2) # Pressure Sensitivity
		C2 = self.ms5611_read_block(0xA4) # Pressure Offset
		C3 = self.ms5611_read_block(0xA6) # Temperature coefficient of pressure sensitivity
		C4 = self.ms5611_read_block(0xA8) # Temperature coefficient of pressure offset
		C5 = self.ms5611_read_block(0xAA) # Reference temperature
		C6 = self.ms5611_read_block(0xAC) # Temperature coefficient of the temperature

		# Pressure acquisition
		self.ms5611_write_byte(0x48)
		D1 = self.ms5611_read_block(0x00)

		# Temperature acquisition
		self.ms5611_write_byte(0x58)
		D2 = self.ms5611_read_block(0x00)

		# Transform arrays into integer
		C1 = C1[0] * 256.0 + C1[1]
		C2 = C2[0] * 256.0 + C2[1]
		C3 = C3[0] * 256.0 + C3[1]
		C4 = C4[0] * 256.0 + C4[1]
		C5 = C5[0] * 256.0 + C5[1]
		C6 = C6[0] * 256.0 + C6[1]
		D1 = D1[0] * 65536 + D1[1] * 256.0 + D1[2]
		D2 = D2[0] * 65536 + D2[1] * 256.0 + D2[2]

		# Calculate temperature
		dT = D2 - C5 * 2**8
		TEMP = 2000 + dT * C6 / 2**23

		# Calculate temperature compensated pressure
		OFF = C2 * 2**16 + (C4 * dT) / 2**7
		SENS = C1 * 2**15 + (C3 * dT) / 2**8
		P = (D1 * SENS / 2**21 - OFF) / 2**15

		# Build human friendly float
		self.temperature = TEMP/100.0
		self.pressure = P/100.0 + PRESSURE_OFFSET
		self.mesureTime = time.time()

	def main(self):
		self.loadDataFile()
		if (time.time() > (self.mesureTime + CACHE_ALIVE)):
			try:
				self.readSensor()
				self.saveDataFile()
			except IOError:
				print 'Error reading sensor'
				self.pressure    = self.data['pressure']
				self.temperature = self.data['temperature']
		print 'Temperature: {0:.2f} *C - Pressure: {1:.2f} mbar'.format(self.temperature, self.pressure)

if __name__ == '__main__':
	MS5611().main()
