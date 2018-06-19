from pinball.controllers.hwgamedevice import OutGameDevice, InGameDevice, PwmOutGameDevice
from pinball.controllers.hwcontroller import BinaryOutHWController, PwmOutHWController


class DummyOutGameDevice(OutGameDevice):
    pass


class DummyInGameDevice(InGameDevice):
    pass


class DummyPwmOutGameDevice(PwmOutGameDevice):
    pass


class DummyController(BinaryOutHWController, PwmOutHWController):
    """
    HW Controller that uses dummy input and output devices.

    These dummy devices will not change any physical state.
    Can be useful for testing purposes.
    """

    def __init__(self):
        BinaryOutHWController.__init__(self)
        PwmOutHWController.__init__(self)
        self._devices = []

    def getHwDevices(self):
        return self._devices[:]

    def getIn(self, name) -> DummyInGameDevice:
        """Creates and returns a new dummy input device."""
        inDevice = DummyInGameDevice(name)
        self._devices.append(inDevice)
        return inDevice

    def getOut(self, name) -> DummyOutGameDevice:
        """Creates and returns a new dummy output device."""
        outDevice = DummyOutGameDevice(name, self)
        self._devices.append(outDevice)
        return outDevice

    def getPwmOut(self, name, intensity: int) -> DummyPwmOutGameDevice:
        """
        Creates and returns a new dummy PWM output device.
        
        :param intensity: initial intensity value 
        """
        outDevice = DummyPwmOutGameDevice(name, self, intensity)
        self._devices.append(outDevice)
        return outDevice

    def sync(self):
        pass

    def activate(self, outDevice: DummyOutGameDevice):
        pass

    def deactivate(self, outDevice: DummyOutGameDevice):
        pass

    def update(self, outDevice: DummyPwmOutGameDevice):
        pass
