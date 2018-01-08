import os
import serial

from pinball.controllers.hwgamedevice import OutGameDevice
from pinball.controllers.hwcontroller import BinaryOutHWController


"""
PowerDriver16

Notes:
    - Communication: serial bus --> Arduino --> Powerdriver

    - Application to be executed on the Arduino can be found in
      projectroot/powerdriver_16_arduino/

    - Communication protocol works when:
       1) Powering up the RaspberryPi
       2) Powering up the Aruidno (after 1 is finished)
       3) Starting the pinball application

       , but is also not yet properly implemented debugged.
"""


class PowerDriver16(BinaryOutHWController):

    def __init__(self, deviceAddress):
        BinaryOutHWController.__init__(self)

        if not os.path.exists(deviceAddress):
            raise RuntimeError("""Serial device "{}" not found, PowerDriver16 will not work.""".format(deviceAddress))

        # Initialize Communication
        self._serial = serial.Serial(deviceAddress, 9600)
        self._serial.write("MY MAGIC PINBALL\r\n".encode())

        self._values = {}
        self._dirtyBanks = set()
        self._devices = []

    def getHwDevices(self):
        return self._devices

    def getOut(self, name, board, bank, pin):
        """Returns a OutGameDevice for a device under the given board, bank, pin.

        @param name Human readable name of the hardware device
        @param board Board identifier of the PowerDriver16 chain
        @param bank Identifier on which bank the device is located, bank A (0) or bank B (1)
        @param pin Pin number of the device on the selected bank
        """
        if (board, bank) not in self._values:
            self._values[(board, bank)] = 0x00
        self._dirtyBanks.add((board, bank))

        device = PowerDriver16OutGameDevice(name, self, board, bank, 1 << pin)
        self._devices.append(device)
        return device

    def activate(self, device):
        """Callback for PowerDriver16OutGameDevice"""
        board = device.board
        bank = device.bank
        self._dirtyBanks.add((board, bank))
        self._values[(board, bank)] |= device.pin

    def deactivate(self, device):
        board = device.board
        bank = device.bank
        self._dirtyBanks.add((board, bank))
        self._values[(board, bank)] &= (~device.pin)

    def sync(self):
        for (board, bank) in self._dirtyBanks:
            self._serial.write([board, bank, self._values[(board, bank)]])
        self._dirtyBanks.clear()


class PowerDriver16OutGameDevice(OutGameDevice):

    def __init__(self, name, hwgamedevice, board, bank, pin):
        OutGameDevice.__init__(self, name, hwgamedevice)
        self.board = board
        self.bank = bank
        self.pin = pin
