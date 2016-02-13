
from .hwgamedevice import InGameDevice
from .hwcontroller import HWController

try:
    import RPi.GPIO as GPIO
except:
    print("No Raspberry Pi GPIO available. Running the code from a pi?!?")
    sys.exit()
GPIO.setmode(GPIO.BCM)


class RaspberryPiInGameDevice(InGameDevice):

    def __init__(self, name, hwdevice, pin):
        InGameDevice.__init__(self, name, hwdevice)
        self._pin = pin


class RaspberryPi(HWController):

    """Represents a Raspberry Pi on which THIS software is running"""

    def __init__(self):
        HWController.__init__(self)
        self._devices = {}  # map of (InGameDevice, oldstate)

    def getIn(self, name, pin):
        if(pin == -1):
            # dummy
            return RaspberryPiInGameDevice(name, self, -1)

        if(pin in self._devices):
            raise Exception("Pin was already instanciated!")

        # Create device, default off
        self._devices[pin] = (RaspberryPiInGameDevice(name, self, pin), 0)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return self._devices[pin][0]

    def sync(self):
        for pin, (device, oldstate) in self._devices.items():
            if GPIO.input(pin) != oldstate:
                self._devices[pin] = (device, not oldstate)
                device.inform(not oldstate)
