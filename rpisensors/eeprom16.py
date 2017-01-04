# -*- coding: utf-8 -*-

import logging

from rpisensors.smbus_wrapper import SMBusWrapper


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
            "Read  [0x%04X] => 0x%02X (%d as byte)",
            register, value, value)
        return value

    def read_word(self, register):
        reg = Eeprom16.address_to_bytes(register)
        self.bus.write_byte_data(self.address, *reg)

        data = self.bus.read_i2c_block_data(self.address, reg[0], 2)
        value = (data[0] << 8) | data[1]

        self.logger.debug(
            "Read  [0x%04X] => [0x%02X, 0x%02X] (%d as word)",
            register, data[0], data[1], value)
        return value

    def write_byte(self, register, data):
        reg = Eeprom16.address_to_bytes(register)
        self.bus.write_i2c_block_data(self.address, reg[0], [reg[1], data])
        self.logger.debug(
            "Write [0x%04X] <= 0x%02X (%d as byte)",
            register, data, data)
