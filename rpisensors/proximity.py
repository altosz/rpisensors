#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

from rpisensors.i2c_device import I2CDevice

from smbus import SMBus


# pylint: disable=C0103


# Default address
VL6180X_I2CADDRESS = 0x29

VL_IDENTIFICATION_MODEL_ID = 0x000
VL_FRESH_OUT_OF_RESET = 0x016


VL_IDENTIFICATION_MODEL_ID_VALUE = 0xB4


class SMBusWrapper(object):

    devices = {}

    @staticmethod
    def open(id):
        if SMBusWrapper.devices.get(id) is None:
            bus = SMBusWrapper._open_bus(id)
            SMBusWrapper.devices[id] = bus

        return SMBusWrapper.devices[id]

    @staticmethod
    def _open_bus(id):
        bus = SMBus()
        bus.open(id)
        return bus

    @staticmethod
    def close(id):
        if SMBusWrapper.devices.get(id) is None:
            return

        SMBusWrapper.devices[id].close()
        del SMBusWrapper.device[id]


class Eeprom16(object):

    def __init__(self, bus_id, address):
        self.bus_id = bus_id
        self.address = address
        self.bus = SMBusWrapper.open(bus_id)

        self.logger = logging.getLogger(
            "{0}, I2C[{1}]:{2:#0x}".format(
                self.__class__.__name__, bus_id, address))

    @staticmethod
    def address_to_bytes(register):
        msb = (register >> 8) & 0xFF
        lsb = register & 0xFF
        return (msb, lsb)

    def read_byte(self, register):
        reg = Eeprom16.address_to_bytes(register)
        self.bus.write_byte_data(self.address, *reg)

        value = self.bus.read_byte(self.address)
        self.logger.debug(
            "Read [0x%04X] => 0x%02X => %d as byte",
            register, value, value)
        return value

    def write_byte(self, register, data):
        reg = Eeprom16.address_to_bytes(register)
        self.bus.write_i2c_block_data(self.address, reg[0], [reg[1], data])
        self.logger.debug(
            "Write [0x%04X] <= 0x%02X <= %d",
            register, data, data)


class VL6180X(Eeprom16):

    def __init__(self, bus_id, address=VL6180X_I2CADDRESS, **kwargs):
        super(VL6180X, self).__init__(bus_id, address, **kwargs)

        self.verify()
        self.prepare()

    def verify(self):
        chip_id = self.read_byte(VL_IDENTIFICATION_MODEL_ID)

        is_vl6180x = chip_id == VL_IDENTIFICATION_MODEL_ID_VALUE

        if is_vl6180x:
            self.logger.debug("VL6180X sensor found: chip id is 0xB4 ")
        else:
            self.logger.warning(
                'No VL6180X sensor found: chip id is 0x%02X, '
                'should be 0x%02X', chip_id, VL_IDENTIFICATION_MODEL_ID_VALUE)

    def prepare(self):
        status = self.read_byte(VL_FRESH_OUT_OF_RESET)

        if status == 1:
            self.logger.debug("System is fresh out of reset")

            self.write_byte(0x0207, 0x01)
            self.write_byte(0x0208, 0x01)
            self.write_byte(0x0096, 0x00)
            self.write_byte(0x0097, 0xfd)
            self.write_byte(0x00e3, 0x00)
            self.write_byte(0x00e4, 0x04)
            self.write_byte(0x00e5, 0x02)
            self.write_byte(0x00e6, 0x01)
            self.write_byte(0x00e7, 0x03)
            self.write_byte(0x00f5, 0x02)
            self.write_byte(0x00d9, 0x05)
            self.write_byte(0x00db, 0xce)
            self.write_byte(0x00dc, 0x03)
            self.write_byte(0x00dd, 0xf8)
            self.write_byte(0x009f, 0x00)
            self.write_byte(0x00a3, 0x3c)
            self.write_byte(0x00b7, 0x00)
            self.write_byte(0x00bb, 0x3c)
            self.write_byte(0x00b2, 0x09)
            self.write_byte(0x00ca, 0x09)
            self.write_byte(0x0198, 0x01)
            self.write_byte(0x01b0, 0x17)
            self.write_byte(0x01ad, 0x00)
            self.write_byte(0x00ff, 0x05)
            self.write_byte(0x0100, 0x05)
            self.write_byte(0x0199, 0x05)
            self.write_byte(0x01a6, 0x1b)
            self.write_byte(0x01ac, 0x3e)
            self.write_byte(0x01a7, 0x1f)
            self.write_byte(0x0030, 0x00)

            self.write_byte(0x0011, 0x10)
            self.write_byte(0x010a, 0x30)
            self.write_byte(0x003f, 0x46)
            self.write_byte(0x0031, 0xFF)
            self.write_byte(0x0040, 0x63)
            self.write_byte(0x002e, 0x01)
            self.write_byte(0x001b, 0x09)
            self.write_byte(0x003e, 0x31)
            self.write_byte(0x0014, 0x24)

            self.write_byte(0x016, 0x00)

    def read_distance(self):
        self.write_byte(0x18, 0x01)

        range = None
        i = 0
        while i < 10:
            i += 1

            status = self.read_byte(0x4F)
            range_status = status & 0x07

            if range_status == 0x04:
                range = self.read_byte(0x62)
                break

            time.sleep(0.2)

        self.write_byte(0x15, 0x07)

        return range


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(name)-20s %(levelname)-8s %(message)s")

    sensor = VL6180X(1)
    for _ in range(10):
        sensor.read_distance()
