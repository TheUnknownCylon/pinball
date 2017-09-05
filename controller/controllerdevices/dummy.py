from .hwgamedevice import OutGameDevice, InGameDevice
from .hwcontroller import HWController


class DummyController(HWController):
    """
    HW Controller that uses dummy input and output devices.

    These dummy devices will not change any physical state.
    Can be useful for testing purposes.
    """

    def __init__(self):
        HWController.__init__(self)
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

    def sync(self):
        pass

    def activate(self, outDevice):
        pass

    def deactivate(self, outDevice):
        pass


class DummyOutGameDevice(OutGameDevice):

    def __init__(self, name, hwdevice):
        OutGameDevice.__init__(self, name, hwdevice)


class DummyInGameDevice(InGameDevice):

    def __init__(self, name, hwdevice, **kwargs):
        InGameDevice.__init__(self, name, hwdevice, **kwargs)
