#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from smbus2 import SMBus


# Default address
VL6180X_I2CADDRESS = 0x29


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


class VL6180X(I2CDevice):

    def __init__(self, bus, address=VL6180X_I2CADDRESS):
        super(VL6180X, self).__init__(bus, address)
        self.logger = logging.getLogger(__name__)
        self.bus = bus


# pylint: disable=C0103

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-30s %(levelname)-8s %(message)s")

    try:
        bus = SMBus()
        bus.open(1)

        sensor = VL6180X(bus)

    finally:
        bus.close()
