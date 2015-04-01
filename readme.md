# Weather sensors demo

Python sniplets to read 2 weather sensors from my Raspberry Pi.

* DHT11 is a low cost, low speed, low accuracy humidity/temperature sensor. It use Adafruit python library.
* MS5611 is an I2C pressure/temperature sensor. It use python-smbus module.

Each sniplet has a JSON file to backup last measure and freeze the value until the sensor is available again.
