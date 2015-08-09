
import time
import sys
from collections import defaultdict

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

class Observable:
    def __init__(self):
        self._observers = defaultdict(list)

    def observe(self, observer, callback):
        self._observers[observer].append(callback)

    def inform(self, state=None):
        """By calling this method, all observers will be informed that there
        has been a change in this observable. This event will be processed
        next tick."""
        for observer in self._observers:
            for callback in self._observers[observer]:
                gameevents.append((callback, self, state))


class GameDevice(Observable):
    """Data class that represents a device in the game."""
    def __init__(self, bank, pin):
        Observable.__init__(self)
        self._bank = bank
        self._pin = pin


class OutGameDevice(GameDevice):
    def set(self, activated):
        if activated:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        self._bank.activate(self._pin)

    def deactivate(self):
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

    def deactivate(self, pin):
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

    def deactivate(self, pin):
        self._dirty = True
        self._values &= (~pin)

    def toggle(self, pin):
        self._dirty = True
        self._values ^= pin

    def refresh(self):
        if(self._dirty):
            data = "> 0x{0:02X} 0x{1:02X} 0x{2:02X}".format(self._board, self._bank, self._values)
            print(data)
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
        return self._devices[pin][0]

    def refresh(self):
        for pin, (device, oldstate) in self._devices.items():
            if GPIO.input(pin) != oldstate:
                self._devices[pin] = (device, not oldstate)
                device.inform(not oldstate)

# Instantiate the hardware
raspberry = RaspberryPi()
bank0A = PowerDriver16(0, 0)
bank0B = PowerDriver16(0, 1)
devices = [raspberry, bank0A, bank0B]

flipper_L_POWER_ENERGIZED = bank0A.getOut(0)
flipper_L_POWER_HOLD = bank0A.getOut(1)
flipper_L_EOS = raspberry.getIn(17)
flipper_R_POWER_ENERGIZED = bank0A.getOut(2)
flipper_R_POWER_HOLD = bank0A.getOut(3)
flipper_R_EOS = raspberry.getIn(18)
flipper_L_BUTTON = raspberry.getIn(23)
flipper_R_BUTTON = raspberry.getIn(24)

l0 = bank0B.getOut(0)
l1 = bank0B.getOut(1)
l2 = bank0B.getOut(2)
l3 = bank0B.getOut(3)
l4 = bank0B.getOut(4)
l5 = bank0B.getOut(5)
l6 = bank0B.getOut(6)
l7 = bank0B.getOut(7)

BLOCK = 0
UNBLOCK = 0
EOSTIMEOUT = 1

class Flipperstate:
    LOW = "Low" #0x00
    ENERGIZED = "Energized" #0x01
    HOLD = "Hold" #0x02
    BLOCKED = "Blocked" #0x03
    EOS_ERROR = "EOS ERROR" #0xFF


class Game():
    def __init__(self):
        self.flipperL = Flipper(flipper_L_BUTTON, flipper_L_EOS, flipper_L_POWER_ENERGIZED, flipper_L_POWER_HOLD)
        self.flipperR = Flipper(flipper_R_BUTTON, flipper_R_EOS, flipper_R_POWER_ENERGIZED, flipper_R_POWER_HOLD)


class Flipper:
    """Class that manages the state of a single flipper."""
    def __init__(self, button, eos, power_energized, power_hold):
        self._state = Flipperstate.LOW
        self._button = button
        self._eos = eos
        self._power_energized = power_energized
        self._power_hold = power_hold

        button.observe(self, self.flipperEvent)
        eos.observe(self, self.flipperEvent)

    def flipperEvent(self, cause, deviceState=None):
        state = self._state
        oldstate = self._state

        if state == Flipperstate.LOW:
            if cause == self._button and deviceState:
                state = Flipperstate.ENERGIZED
            # elif cause == self._eos and deviceState:
                # state = Flipperstate.EOS_ERROR
            elif cause == BLOCK and deviceState:
                state = Flipperstate.BLOCKED

        elif state == Flipperstate.ENERGIZED:
            if cause == self._button and not deviceState:
                state = Flipperstate.LOW
            elif cause == self._eos and deviceState:
                state = Flipperstate.HOLD
            elif cause == EOSTIMEOUT:
                print("WARNING: EOS NOT DETECTED, ASSUMING EOS HIGH")
                state = Flipperstate.HOLD

        elif state == Flipperstate.HOLD:
            if cause == self._button and not deviceState:
                state = Flipperstate.LOW
            elif cause == self._eos and not deviceState:
                state = Flipperstate.ENERGIZED

        elif state == Flipperstate.BLOCKED:
            if cause == UNBLOCK:
                state = Flipperstate.LOW

        if state != oldstate:
            self._state = state
            self._power_energized.set(state == Flipperstate.ENERGIZED)
            self._power_hold.set(state == Flipperstate.HOLD)


game = Game()

def tick():
    while gameevents:
        (event, cause, newstate) = gameevents.pop(0)
        event(cause, newstate)


def sync():
    for bank in devices:
        bank.refresh()

import threading
frames = 0
lock = threading.Lock()
def printFPS():
    t = threading.Timer(1.0, printFPS)
    t.setDaemon(True)
    t.start()
    global frames
    with lock:
        tmp = frames
        frames = 0
        # print("FPS: {}".format(tmp))
printFPS()

while True:
    tick()
    sync()
    time.sleep(0.01)
    with lock:
        frames+=1

