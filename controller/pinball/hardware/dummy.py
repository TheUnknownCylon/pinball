from pinball.hardware.controller import OutputController
from pinball.hardware.hwdevice import OutputDevice, InputDevice, PwmOutputDevice


class DummyOutputDevice(OutputDevice):
    def activate(self):
        pass

    def deactivate(self):
        pass


class DummyInputDevice(InputDevice):
    pass


class DummyPwmOutputDevice(PwmOutputDevice):
    pass


class DummyController(OutputController):
    """
    HW Controller that uses dummy input and output devices.

    These dummy devices will not change any physical state.
    Can be useful for testing purposes.
    """

    def __init__(self):
        OutputController.__init__(self)
        self._devices = []

    def getDevices(self):
        return self._devices[:]

    def getIn(self, name) -> DummyInputDevice:
        """Creates and returns a new dummy input device."""
        inDevice = DummyInputDevice(name)
        self._devices.append(inDevice)
        return inDevice

    def getOut(self, name) -> DummyOutputDevice:
        """Creates and returns a new dummy output device."""
        outDevice = DummyOutputDevice(name)
        self._devices.append(outDevice)
        return outDevice

    def getPwmOut(self, name, maxIntensity: int) -> DummyPwmOutputDevice:
        """
        Creates and returns a new dummy PWM output device.
        
        :param maxIntensity: maximum intensity valuet that can be set
        """
        outDevice = DummyPwmOutputDevice(name, self, maxIntensity)
        self._devices.append(outDevice)
        return outDevice

    def sync(self):
        pass

    def update(self, device: DummyOutputDevice):
        pass
