from pinball.controllers.hwgamedevice import OutGameDevice, InGameDevice, PwmOutGameDevice
from pinball.controllers.hwcontroller import BinaryOutHWController, PwmOutHWController


class DummyController(BinaryOutHWController, PwmOutHWController):
    """
    HW Controller that uses dummy input and output devices.

    These dummy devices will not change any physical state.
    Can be useful for testing purposes.
    """

    def __init__(self):
        BinaryOutHWController.__init__(self)
        PwmOutHWController.__init__(self)
        self._devices = []  # map of (GameDevice, oldstate)

    def getHwDevices(self):
        return self._devices[:]

    def getIn(self, name):
        inDevice = DummyInGameDevice(name, self)
        self._devices.append(inDevice)
        return inDevice

    def getOut(self, name):
        outDevice = DummyOutGameDevice(name, self)
        self._devices.append(outDevice)
        return outDevice

    def getPwmOut(self, name, intensity):
        outDevice = DummyPwmOutGameDevice(name, self, intensity)
        self._devices.append(outDevice)
        return outDevice

    def sync(self):
        pass

    def activate(self, outDevice):
        pass

    def deactivate(self, outDevice):
        pass

    def update(self, outDevice):
        pass


class DummyOutGameDevice(OutGameDevice):
    pass


class DummyInGameDevice(InGameDevice):
    pass

class DummyPwmOutGameDevice(PwmOutGameDevice):
    pass
