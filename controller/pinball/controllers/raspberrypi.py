from pinball.controllers.hwgamedevice import InGameDevice
from pinball.controllers.hwcontroller import HWController

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


class RaspberryPiInGameDevice(InGameDevice):

    def __init__(self, name, pin: int, **kwargs) -> None:
        InGameDevice.__init__(self, name, **kwargs)
        self._pin = pin


class RaspberryPi(HWController):
    """Represents a Raspberry Pi on which THIS software is running.
    Can be used to read input devices."""

    def __init__(self):
        HWController.__init__(self)
        self._devices: Dict[RaspberryPiInGameDevice, bool] = {} # dict of (InGameDevice, oldstate)

    def getHwDevices(self):
        return list([x[0] for x in self._devices.values()])

    def getIn(self, name, pin: int, **kwargs):
        if(pin == -1):
            return RaspberryPiInGameDevice(name, -1, **kwargs)

        if(pin in self._devices):
            raise Exception("Pin was already instanciated!")

        # Create device, default off
        self._devices[pin] = (RaspberryPiInGameDevice(name, pin, **kwargs), 0)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return self._devices[pin][0]

    def sync(self):
        for pin, (device, oldstate) in self._devices.items():
            if GPIO.input(pin) != oldstate:
                self._devices[pin] = (device, not oldstate)
                device.inform(not oldstate)
