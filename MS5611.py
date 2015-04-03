#!/usr/bin/python

import time
import json
from smbus import SMBus

# Configuration
busSelection = 1
MS5611Address = 0x77
backupFile = "MS5611.json"

def ms5611_read_block(command):
	data = bus.read_i2c_block_data(MS5611Address, command)
	time.sleep(0.05)
	return data
	
def ms5611_write_byte(data):
	bus.write_byte(MS5611Address, data)
	time.sleep(0.05)

try:
	# Bus init
	bus = SMBus(busSelection)

	# Read calibration data
	C1 = ms5611_read_block(0xA2) # Pressure Sensitivity
	C2 = ms5611_read_block(0xA4) # Pressure Offset
	C3 = ms5611_read_block(0xA6) # Temperature coefficient of pressure sensitivity
	C4 = ms5611_read_block(0xA8) # Temperature coefficient of pressure offset
	C5 = ms5611_read_block(0xAA) # Reference temperature
	C6 = ms5611_read_block(0xAC) # Temperature coefficient of the temperature

	# Pressure acquisition
	ms5611_write_byte(0x48)
	D1 = ms5611_read_block(0x00)

	# Temperature acquisition
	ms5611_write_byte(0x58)
	D2 = ms5611_read_block(0x00)

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
	temperature = TEMP/100.0
	pressure = P/100.0
	live = True
except IOError:
	temperature = None
	pressure = None
	
# Fallback to last value on error
if temperature is None or pressure is None or pressure < 800.0 or pressure > 1200.0:
	# Fallback to last value on error
	file = open(backupFile, "r")
	data = json.load(file)
	file.close()
	pressure = data['pressure']
	temperature = data['temperature']
	live = False

# Display
print 'Temperature: {0:.2f} *C - Pressure: {1:.2f} mbar - Live: {2}'.format(temperature, pressure, live)

# Save for future
if live:
	file = open(backupFile, "w")
	data = {'temperature': temperature, 'pressure': pressure}
	json.dump(data, file)
	file.close()
