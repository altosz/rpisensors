#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import logging
import time

from rpisensors.i2c_device import I2CDevice


# pylint: disable=C0103


# Default address
BMP180_I2CADDR = 0x77

# Operating modes
BMP180_ULTRALOWPOWER = 0
BMP180_STANDARD = 1
BMP180_HIGHRES = 2
BMP180_ULTRAHIGHRES = 3

# Registers
BMP180_CAL_AC1 = 0xAA
BMP180_CAL_AC2 = 0xAC
BMP180_CAL_AC3 = 0xAE
BMP180_CAL_AC4 = 0xB0
BMP180_CAL_AC5 = 0xB2
BMP180_CAL_AC6 = 0xB4
BMP180_CAL_B1 = 0xB6
BMP180_CAL_B2 = 0xB8
BMP180_CAL_MB = 0xBA
BMP180_CAL_MC = 0xBC
BMP180_CAL_MD = 0xBE
BMP180_CHIP_ID = 0xD0
BMP180_CONTROL = 0xF4
BMP180_TEMPDATA = 0xF6
BMP180_PRESSUREDATA = 0xF6

BMP180_CHIP_ID_VALUE = 0x55

# Commands
BMP180_READTEMPCMD = 0x2E
BMP180_READPRESSURECMD = 0x34


class BMP180(I2CDevice):

    def __init__(
            self, bus, address=BMP180_I2CADDR, mode=BMP180_STANDARD, **kwargs):
        super(BMP180, self).__init__(bus, address, **kwargs)
        self.mode = mode

        self.verify()
        self.load_calibration()

        self.temperature = None
        self.pressure = None

    def verify(self):
        chip_id = self.read_uint8(BMP180_CHIP_ID)

        is_bmp180 = chip_id == BMP180_CHIP_ID_VALUE

        if is_bmp180:
            self.logger.debug('Bosch BMP180 sensor found: chip id is 0x55')
        else:
            self.logger.warning(
                'No Bosch BMP180 sensor found: chip id is 0x%02X, '
                'should be 0x%02X', chip_id, BMP180_CHIP_ID_VALUE)

        return is_bmp180

    def load_calibration(self):
        data = [
            ('AC1', 'read_int16', BMP180_CAL_AC1),
            ('AC2', 'read_int16', BMP180_CAL_AC2),
            ('AC3', 'read_int16', BMP180_CAL_AC3),
            ('AC4', 'read_uint16', BMP180_CAL_AC4),
            ('AC5', 'read_uint16', BMP180_CAL_AC5),
            ('AC6', 'read_uint16', BMP180_CAL_AC6),
            ('B1', 'read_int16', BMP180_CAL_B1),
            ('B2', 'read_int16', BMP180_CAL_B2),
            ('MB', 'read_int16', BMP180_CAL_MB),
            ('MC', 'read_int16', BMP180_CAL_MC),
            ('MD', 'read_int16', BMP180_CAL_MD),
        ]

        self.calibration = {}
        for key, func, address in data:
            value = getattr(self, func)(address)
            self.calibration[key] = value

        for key, _, _ in data:
            self.logger.debug(
                "Calibration register %s = %s", key, self.calibration[key])

    def _read_raw_temperature(self):
        self.write_int8(BMP180_CONTROL, BMP180_READTEMPCMD)
        time.sleep(0.005)

        raw = self.read_uint16(BMP180_TEMPDATA)

        self.logger.debug('Raw temperature is 0x%04X (%d)', raw & 0xFFFF, raw)
        return raw

    def _read_raw_pressure(self):
        self.write_int8(
            BMP180_CONTROL, BMP180_READPRESSURECMD + (self.mode << 6))

        delay_values = {
            BMP180_ULTRALOWPOWER: 0.005,
            BMP180_STANDARD: 0.008,
            BMP180_HIGHRES: 0.014,
            BMP180_ULTRAHIGHRES: 0.026,
        }
        time.sleep(delay_values[self.mode])

        msb = self.read_uint8(BMP180_PRESSUREDATA)
        lsb = self.read_uint8(BMP180_PRESSUREDATA + 1)
        xlsb = self.read_uint8(BMP180_PRESSUREDATA + 2)
        raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)

        self.logger.debug('Raw pressure is 0x%04X (%d)', raw & 0xFFFF, raw)
        return raw

    def read_temperature(self):
        UT = self._read_raw_temperature()
        X1 = ((UT - self.calibration['AC6']) * self.calibration['AC5']) >> 15
        X2 = (self.calibration['MC'] << 11) // (X1 + self.calibration['MD'])
        B5 = X1 + X2
        temperature = ((B5 + 8) >> 4) / 10.0

        self.logger.debug('Calibrated temperature is %0.2f C', temperature)
        return temperature

    def read_temperature_and_pressure(self):
        UT = self._read_raw_temperature()
        UP = self._read_raw_pressure()

        X1 = ((UT - self.calibration['AC6']) * self.calibration['AC5']) >> 15
        X2 = (self.calibration['MC'] << 11) // (X1 + self.calibration['MD'])
        B5 = X1 + X2
        temperature = ((B5 + 8) >> 4) / 10.0

        B6 = B5 - 4000
        X1 = (self.calibration['B2'] * (B6 * B6) >> 12) >> 11
        X2 = (self.calibration['AC2'] * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.calibration['AC1'] * 4 + X3) << self.mode) + 2) // 4
        X1 = (self.calibration['AC3'] * B6) >> 13
        X2 = (self.calibration['B1'] * ((B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.calibration['AC4'] * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> self.mode)

        p = 0
        if B7 < 0x80000000:
            p = (B7 * 2) // B4
        else:
            p = (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        pressure = p + ((X1 + X2 + 3791) >> 4)

        self.logger.debug('Calibrated temperature is %0.2f C', temperature)
        self.logger.debug('Calibrated pressure is %d Pa', pressure)

        return (temperature, pressure)


def pressure_to_altitude(pressure, sealevel_pa=101325.0):
    altitude = 44330.0 * (1.0 - pow(pressure / sealevel_pa, (1.0 / 5.255)))
    return altitude


def pressure_Pa_to_mmHg(pa):
    return pa * 760 / 101325


if __name__ == "__main__":
    from smbus import SMBus

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)-20s %(levelname)-8s %(message)s")

    try:
        bus = SMBus()
        bus.open(1)

        sensor = BMP180(bus, bus_id=1, little_endian=False)
        temp, pa = sensor.read_temperature_and_pressure()
        alt = pressure_to_altitude(pa)
        mmHg = pressure_Pa_to_mmHg(pa)

        print "Temperature is %0.2f C" % (temp)
        print "Pressure is %d Pa (%0.2f mmHg)" % (pa, mmHg)
        print "Altitude (based on pressure) is %d m" % (alt)

    finally:
        bus.close()
