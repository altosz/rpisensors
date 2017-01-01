#!/usr/bin/env python
# -*- coding: utf-8 -*-


class I2CDevice(object):

    def __init__(self, bus, address):
        self.bus = bus
        self.address = address

    def read_uint8(self, register):
        return self.bus.read_byte_data(self.address, register)

    def read_uint16(self, register):
        return self.bus.read_word_data(self.address, register)

    def read_int16(self, register):
        value = self.read_uint16(register)
        if value >= 0x8000:
            value = -(66635 - value + 1)
        return value
