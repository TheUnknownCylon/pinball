
import time
import sys

try:
    import RPi.GPIO as GPIO
except:
    print("No Raspberry Pi GPIO available. Running the code from a pi?!?")
    sys.exit()
GPIO.setmode(GPIO.BCM)

ser = None
try:
    import serial
    ser = serial.Serial('/dev/ttyAMA0', 9600)
except:
    print("NO SERIAL DEVICE SET! SENDING DATA TO STDOUT INSTEAD!")


# Variable that holds all events that need to be processed during the next frame
gameevents = []

class GameDevice:
    """Data class that represents a device in the game."""
    def __init__(self, bank, pin):
        self._bank = bank
        self._pin = pin


class OutGameDevice(GameDevice):
    def activate(self):
        self._bank.activate(self._pin)

    def deactiate(self):
        self._bank.deactivate(self._pin)

    def toggle(self):
        self._bank.toggle(self._pin)


class InGameDevice(GameDevice):
    pass


class ControlDevice:
    def refresh(self):
        """
        Syncs the hardware with the current software state.
        1. Output devices will get new instructions.
        2. The state of the input devices is read, and new events are triggered if
           there were changes.
        """
        raise NotImlemented()

    def activate(self, pin):
        raise NotImlemented()

    def deactiate(self, pin):
        raise NotImlemented()

    def toggle(self, pin):
        raise NotImlemented()


class PowerDriver16(ControlDevice):
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

    def deactiate(self, pin):
        self._dirty = True
        self._values &= (~pin)

    def toggle(self, pin):
        self._dirty = True
        self._values ^= pin

    def refresh(self):
        if(self._dirty):
            # data = "> 0x{0:02X} 0x{1:02X} 0x{2:02X}".format(self._board, self._bank, self._values)
            # print(data)
            if ser:
                ser.write(bank._board)
                ser.write(bank._bank)
                ser.write(bank._value)
        self._dirty = False

    def __str__(self):
        return "[{0} {1}] [ {2:08b} ]".format(self._board, "B" if self._bank else "A", self._values)


class RaspberryPi(ControlDevice):
    """Represents a Raspberry Pi on which THIS software is running"""
    pass

    def __init__(self):
        self._devices = {}

    def getIn(self, pin):
        if(pin in self._devices):
            raise Exception("Pin was already instanciated!")
        self._devices[pin] = (InGameDevice(self, pin), 0)  #default off
        GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
        return self._devices[pin]

    def refresh(self):
        for pin, (device, oldstate) in self._devices.items():
            print("P: {}".format(GPIO.input(pin)))
            if GPIO.input(pin) != oldstate:
                # print("!!!!!!!")
                self._devices[pin] = (device, not oldstate)
                gameevents.append(device)


# Instantiate the hardware
raspberry = RaspberryPi()
bank0A = PowerDriver16(0, 0)
bank0B = PowerDriver16(0, 1)
devices = [raspberry, bank0A, bank0B]

flipper_L_HIGH = bank0A.getOut(0)
flipper_L_LOW = bank0A.getOut(1)
flipper_L_EOS = raspberry.getIn(17)
flipper_R_HIGH = bank0A.getOut(2)
flipper_R_LOW = bank0A.getOut(3)
# flipper_R_EOS = raspberry.getIn(24)

l0 = bank0B.getOut(0)
l1 = bank0B.getOut(1)
l2 = bank0B.getOut(2)
l3 = bank0B.getOut(3)
l4 = bank0B.getOut(4)
l5 = bank0B.getOut(5)
l6 = bank0B.getOut(6)
l7 = bank0B.getOut(7)

def tick():
    l4.toggle()

    while gameevents:
        event = gameevents.pop(0)
        # print("> Process event {}".format(event))

def sync():
    for bank in devices:
        bank.refresh()

while True:
    tick()
    sync()
    time.sleep(0.05)

