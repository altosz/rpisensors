#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import logging


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

# Commands
BMP180_READTEMPCMD = 0x2E
BMP180_READPRESSURECMD = 0x34


class I2CDevice(object):

    def __init__(self, bus, address, little_endian=False):
        self.logger = logging.getLogger(
            "{0}, I2C[{1}]:{2:#0x}".format(
                self.__class__.__name__, 1, address))
        self.bus = bus
        self.address = address

        if little_endian:
            self._read16 = self._read16_little_endian
        else:
            self._read16 = self._read16_big_endian

    def read_uint8(self, register):
        value = self.bus.read_byte_data(self.address, register)
        self.logger.debug(
            "Read [0x%02X] => 0x%04X => %d as uint8",
            register, value, value)
        return value

    def _read16_little_endian(self, register):
        value = self.bus.read_word_data(self.address, register)
        return value

    def _read16_big_endian(self, register):
        value = self.bus.read_word_data(self.address, register)
        value = ((value << 8) & 0xFF00) + (value >> 8)
        return value


    def read_uint16(self, register):
        value = self._read16(register)
        self.logger.debug(
            "Read [0x%02X, 0x%02X] => 0x%04X => %d as uint16",
            register, register + 1, value, value)
        return value

    def read_int16(self, register):
        value = self._read16(register)

        result = value
        if result >= 0x8000:
            result -= 65536

        self.logger.debug(
            "Read [0x%02X, 0x%02X] => 0x%04X => %d as int16",
            register, register + 1, value, result)
        return result


class BMP180(I2CDevice):

    def __init__(
            self, bus, address=BMP180_I2CADDR, mode=BMP180_STANDARD, **kwargs):
        super(BMP180, self).__init__(bus, address, **kwargs)
        self.mode = mode

        chip_id = self.read_uint8(BMP180_CHIP_ID)
        assert chip_id == 0x55

        self.load_calibration()

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


# pylint: disable=C0103

if __name__ == "__main__":
    from smbus2 import SMBus

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)-20s %(levelname)-8s %(message)s")

    try:
        bus = SMBus()
        bus.open(1)

        sensor = BMP180(bus, little_endian=False)

    finally:
        bus.close()
