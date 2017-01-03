#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from rpisensors.i2c_device import I2CDevice


# Default address
VL6180X_I2CADDRESS = 0x29


class VL6180X(I2CDevice):

    def __init__(self, bus, address=VL6180X_I2CADDRESS):
        super(VL6180X, self).__init__(bus, address)
        self.logger = logging.getLogger(__name__)
        self.bus = bus


# pylint: disable=C0103

if __name__ == "__main__":
    from smbus import SMBus

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-30s %(levelname)-8s %(message)s")

    try:
        bus = SMBus()
        bus.open(1)

        sensor = VL6180X(bus)

    finally:
        bus.close()
