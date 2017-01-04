rpisensors
==========

This Python module is a collection of classes to enable Raspberry PI sensors support. Module also contains core classes to be used for interaction with I2C devices and also 16-bit EEPROM modules.

Supported sensors and measurements:

1. Bosch BMP180
	
	* temperature (Celsius degrees)
	* pressure (Pa)

2. ST VL6180X

	* distance (mm)
	* ambient light (lux)


Dependencies
------------

* smbus-cffi
::

  See https://github.com/bivab/smbus-cffi/blob/master/README.rst for install instructions.

Installation
------------

1. pip install from PyPi
::

  pip install rpisensors

2. pip install from git
::

  pip install git+https://github.com/altosz/rpisensors.git

3. Clone the repository and run setup.py
::

  git clone https://github.com/altosz/rpisensors.git
  python setup.py install

 Tests
 -----

If you have a sensor connected to Raspberry PI 3 (on I2C bus 1), you may run
  
  python -m rpisensors.bmp180
  python -m rpisensors.proximity

The output will show the results of measurement.
If you have sensors connected to I2C bus 0, you may test the sensor from python console:
::

  >>> from rpisensors import BMP180
  >>> sensor = BMP180(0)
  >>> print sensor.read_temperature() 

Bug Reporting
-------------

To submit a bugreport use the GitHub bugtracker for the project:

  https://github.com/altosz/rpisensors/issues

Development
-----------

You may use I2CDevice class as a base for I2C devices. Or Eeprom16 for devices using 16-bit eeprom.

Authors
-------

* Alexei Tishin (altos.z@gmail.com)

Copyright
---------

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

See LICENSE for full license text
