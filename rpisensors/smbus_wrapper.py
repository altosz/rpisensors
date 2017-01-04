# -*- coding: utf-8 -*-

from smbus import SMBus


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
