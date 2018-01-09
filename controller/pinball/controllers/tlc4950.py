import logging
import smbus

from pinball.controllers.hwgamedevice import PwmOutGameDevice
from pinball.controllers.hwcontroller import PwmOutHWController

TLC4950_MAX_INTENSITY = (1 << 12) - 1


class Tlc4950(PwmOutHWController):
    def __init__(self, address):
        PwmOutHWController.__init__(self)

        self._bus = smbus.SMBus(1)
        self._address = address

        self._devices = []
        self._dirty = set()

    def getHwDevices(self):
        return self._devices[:]

    def sync(self):
        i = 0
        while self._dirty:
            i = i + 1
            pwmOutDevice = self._dirty.pop()

            update = ((1 << 7) if not self._dirty else 0)
            b1 = update | (pwmOutDevice._pin << 4) | (
                pwmOutDevice._intensity >> 8)
            b2 = pwmOutDevice._intensity & 0xFF
            print("{}: {:08b} {:08b}".format(i, b1, b2))
            self._bus.write_i2c_block_data(self._address, b1, [b2])

    def getPwmOut(self, name, pin):
        outDevice = Tlc4950OutGameDevice(name, self, pin)
        self._devices.append(outDevice)
        return outDevice

    def update(self, pwmOutDevice):
        print("u {}".format(pwmOutDevice._pin))
        self._dirty.add(pwmOutDevice)


class Tlc4950OutGameDevice(PwmOutGameDevice):
    def __init__(self, name, hwdevice, pin):
        PwmOutGameDevice.__init__(self, name, hwdevice, TLC4950_MAX_INTENSITY)
        self._pin = pin
