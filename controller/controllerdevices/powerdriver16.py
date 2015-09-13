
from .hwgamedevice import OutGameDevice
from .hwcontroller import HWController

ser = None
try:
    import serial
    ser = serial.Serial('/dev/ttyAMA0', 9600)
    ser.write("MY MAGIC PINBALL\r\n".encode())
except Exception as e:
    print(e)
    print("NO SERIAL DEVICE SET! SENDING DATA TO STDOUT INSTEAD!")


class PowerDriver16(HWController):

    def __init__(self, board, bank):
        self._board = board
        self._bank = bank
        self._values = 0x00
        self._dirty = True

    def getOut(self, pin):
        return OutGameDevice(self, 1 << pin)

    def getIn(self, pin):
        return InGameDevice(self, 1 << pin)

    def activate(self, pin):
        self._dirty = True
        self._values |= pin

    def deactivate(self, pin):
        self._dirty = True
        self._values &= (~pin)

    def toggle(self, pin):
        self._dirty = True
        self._values ^= pin

    def sync(self):
        if(self._dirty):
            data = "> 0x{0:02X} 0x{1:02X} 0x{2:02X}".format(
                self._board, self._bank, self._values)
            print(data)
            if ser:
                ser.write([self._board, self._bank, self._values])
        self._dirty = False

    def __str__(self):
        return "[{0} {1}] [ {2:08b} ]".format(self._board, "B" if self._bank else "A", self._values)
