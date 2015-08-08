
import time
import serial

ser = None
try:
    ser = serial.Serial('/dev/tty.ACM0', 9600)
except:
    print("NO SERIAL DEVICE SET! SENDING DATA TO STDOUT INSTEAD!")

def sendState(bank):
    data = "> 0x{0:02X} 0x{1:02X} 0x{2:02X}".format(bank._board, bank._bank, bank._values)
    print(data)
    if ser:
        ser.write(bank._board)
        ser.write(bank._bank)
        ser.write(bank._value)



class DeviceOut:
    def __init__(self, bank, pin):
        self._bank = bank
        self._pin = pin

    def activate(self):
        self._bank.activate(self._pin)

    def deactiate(self):
        self._bank.deactivate(self._pin)

    def toggle(self):
        self._bank.toggle(self._pin)

class Bank:
    def __init__(self, board, bank):
        self._board = board
        self._bank = bank
        self._values = 0x00
        self._dirty = True

    def getDevice(self, pin):
        return DeviceOut(self, 1 << pin)

    def print(self):
        print(" [{0} {1}] [ {2:08b} ]".format(self._board, "B" if self._bank else "A", self._values))

    def activate(self, pin):
        self._dirty = True
        self._values |= pin

    def deactiate(self, pin):
        self._dirty = True
        self._values &= (~pin)

    def toggle(self, pin):
        self._dirty = True
        self._values ^= pin

    def getState(self):
        """Returns the current dirty state and binary state. Resets the dirty state."""
        dirty = self._dirty
        self._dirty = False
        return dirty, self._values

bank0A = Bank(0, 0)
bank0B = Bank(0, 1)
banks = [bank0A, bank0B]

flipper_L_HIGH = bank0A.getDevice(0)
flipper_L_LOW = bank0A.getDevice(1)
flipper_R_HIGH = bank0A.getDevice(2)
flipper_R_LOW = bank0A.getDevice(3)

l0 = bank0B.getDevice(0)
l1 = bank0B.getDevice(1)
l2 = bank0B.getDevice(2)
l3 = bank0B.getDevice(3)
l4 = bank0B.getDevice(4)
l5 = bank0B.getDevice(5)
l6 = bank0B.getDevice(6)
l7 = bank0B.getDevice(7)

def tick():
    bank0A.print()
    bank0B.print()
    l4.toggle()

def sync():
    for bank in banks:
        dirty, state = bank.getState()
        if dirty:
            sendState(bank)

while True:
    tick()
    sync()


