import logging
from smbus2 import SMBus

from typing import List, Set

from pinball.controllers.hwgamedevice import PwmOutGameDevice
from pinball.controllers.hwcontroller import PwmOutHWController

TLC4950_MAX_INTENSITY = (1 << 12) - 1


class Tlc4950(PwmOutHWController):
    def __init__(self, address: int) -> None:
        """
        Constructs a new TLC4950.

        :param address: I2C address of the TLC4950 device.
        """
        PwmOutHWController.__init__(self)

        self._bus = SMBus(1)
        self._address = address

        self._devices: List['Tlc4950OutGameDevice'] = []
        self._dirty: Set['Tlc4950OutGameDevice'] = set()

    def getHwDevices(self):
        return self._devices[:]

    def sync(self):
        if not self._dirty:
            return

        i = 0
        b = []
        while self._dirty:
            i = i + 1
            pwmOutDevice = self._dirty.pop()

            # update = ((1 << 7) if not self._dirty else 0)
            update = 0b10000000
            b1 = update | (pwmOutDevice._pin << 4) | (
                pwmOutDevice._intensity >> 8)
            b2 = pwmOutDevice._intensity & 0xFF
            b.append(b1)
            b.append(b2)

        self._bus.write_i2c_block_data(self._address, b[0], b[1:])

    def getPwmOut(self, name, pin: int):
        outDevice = Tlc4950OutGameDevice(name, self, pin)
        self._devices.append(outDevice)
        return outDevice

    def update(self, pwmOutDevice: 'Tlc4950OutGameDevice'):
        self._dirty.add(pwmOutDevice)


class Tlc4950OutGameDevice(PwmOutGameDevice):
    def __init__(self, name, hwdevice: Tlc4950, pin: int) -> None:
        PwmOutGameDevice.__init__(self, name, hwdevice, TLC4950_MAX_INTENSITY)
        self._pin = pin
