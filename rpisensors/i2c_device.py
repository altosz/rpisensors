#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


class I2CDevice(object):

    def __init__(self, bus, address, bus_id='?', little_endian=False):
        self.bus = bus
        self.address = address

        if little_endian:
            self._read16 = self._read16_little_endian
        else:
            self._read16 = self._read16_big_endian

        self.logger = logging.getLogger(
            "{0}, I2C[{1}]:{2:#0x}".format(
                self.__class__.__name__, bus_id, address))

    def read_uint8(self, register):
        value = self.bus.read_byte_data(self.address, register)
        self.logger.debug(
            "Read [0x%02X] => 0x%02X => %d as uint8",
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

    def write_int8(self, register, value):
        self.bus.write_byte_data(self.address, register, value)
        self.logger.debug(
            "Write [0x%02X] <= 0x%02X <= %d as int8",
            register, value, value)
