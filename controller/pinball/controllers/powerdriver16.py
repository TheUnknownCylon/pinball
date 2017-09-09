import os
import serial

from pinball.controllers.hwgamedevice import OutGameDevice
from pinball.controllers.hwcontroller import HWController


"""
PowerDriver16

Notes:
    - Only works when directly executed from a RaspberryPi

    - Communication: RPI --> Arduino --> Powerdriver

    - Application to be executed on the Raspbery can be found in
      projectroot/powerdriver_16_arduino/

    - Communication protocol works when:
       1) Powering up the RaspberryPi
       2) Powering up the Aruidno (after 1 is finished)
       3) Starting the pinball application

       , but is also not yet properly implemented debugged.

    - Requires write-permissions to /dev/ttyAMA0
"""

serial_device_file = '/dev/ttyAMA0'
if not os.path.exists(serial_device_file):
    raise RuntimeError("""Serial device "{}" not found, PowerDriver16 will not work.""".format(serial_device_file))


# Initialize Communication
ser = serial.Serial('/dev/ttyAMA0', 9600)
ser.write("MY MAGIC PINBALL\r\n".encode())


class PowerDriver16(HWController):

    def __init__(self, board, bank):
        HWController.__init__(self)
        self._board = board
        self._bank = bank
        self._values = 0x00
        self._dirty = True
        self._devices = []

    def getHwDevices(self):
        return self._devices

    def getOut(self, name, pin):
        device = PowerDriver16OutGameDevice(name, self, 1 << pin)
        self._devices.append(device)
        return device

    def activate(self, device):
        self._dirty = True
        self._values |= device.pin

    def deactivate(self, device):
        self._dirty = True
        self._values &= (~device.pin)

    def sync(self):
        if(self._dirty):
            ser.write([self._board, self._bank, self._values])
        self._dirty = False

    def __str__(self):
        return "[{0} {1}] [ {2:08b} ]".format(
            self._board, "B" if self._bank else "A", self._values)


class PowerDriver16OutGameDevice(OutGameDevice):

    def __init__(self, name, hwgamedevice, pin):
        OutGameDevice.__init__(self, name, hwgamedevice)
        self.pin = pin
