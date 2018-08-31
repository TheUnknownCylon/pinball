from __future__ import annotations

import os
import serial

from pinball.hardware.hwdevice import OutputDevice
from pinball.hardware.controller import OutputController
from typing import Set, Tuple, Dict, List
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


class PowerDriver16(OutputController):
    def __init__(self, deviceAddress: str) -> None:
        """
        Constructs a controller for the PowerDriver 16.

        :param deviceAddress: device address for serial communication to the PowerDriver16 (e.g. /dev/ttyUSB0)
        """
        OutputController.__init__(self)

        if not os.path.exists(deviceAddress):
            raise RuntimeError(
                """Serial device "{}" not found, PowerDriver16 will not work.""".
                format(deviceAddress))

        # Initialize Communication
        self._serial = serial.Serial(deviceAddress, 9600)
        self._serial.write("MY MAGIC PINBALL\r\n".encode())

        self._values: Dict[Tuple[int, int], int] = {}
        self._dirtyBanks: Set[Tuple[int, int]] = set()
        self._devices: List[PowerDriver16OutputDevice] = []

    def getHwDevices(self):
        return self._devices

    def getOut(self, name, board: int, bank: int, pin: int):
        """Returns a OutputDevice for a device under the given board, bank, pin.

        :param name: Human readable name of the hardware device
        :param board: Board identifier of the PowerDriver16 chain
        :param bank: Identifier on which bank the device is located, bank A (0) or bank B (1)
        :param pin: Pin number of the device on the selected bank
        """
        if (board, bank) not in self._values:
            self._values[(board, bank)] = 0x00
        self._dirtyBanks.add((board, bank))

        device = PowerDriver16OutputDevice(name, self, board, bank, 1 << pin)
        self._devices.append(device)
        return device

    def activate(self, device: PowerDriver16OutputDevice):
        board = device.board
        bank = device.bank
        self._dirtyBanks.add((board, bank))
        self._values[(board, bank)] |= device.pin

    def deactivate(self, device: PowerDriver16OutputDevice):
        board = device.board
        bank = device.bank
        self._dirtyBanks.add((board, bank))
        self._values[(board, bank)] &= (~device.pin)

    def sync(self):
        for (board, bank) in self._dirtyBanks:
            self._serial.write([board, bank, self._values[(board, bank)]])
        self._dirtyBanks.clear()


class PowerDriver16OutputDevice(OutputDevice):
    def __init__(self, name, controller: PowerDriver16, board: int, bank: int,
                 pin: int) -> None:
        OutputDevice.__init__(self, name)
        self.board = board
        self.bank = bank
        self.pin = pin
