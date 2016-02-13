
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
        HWController.__init__(self)
        self._board = board
        self._bank = bank
        self._values = 0x00
        self._dirty = True

    def getOut(self, name, pin):
        return PowerDriver16OutGameDevice(name, self, 1 << pin)

    def activate(self, device):
        self._dirty = True
        self._values |= device.pin

    def deactivate(self, device):
        self._dirty = True
        self._values &= (~device.pin)

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


class PowerDriver16OutGameDevice(OutGameDevice):

    def __init__(self, name, hwgamedevice, pin):
        OutGameDevice.__init__(self, name, hwgamedevice)
        self.pin = pin