
from e_observable import Observable


class GameDevice(Observable):

    """Data class that represents a two-state hardware device in the game."""

    def __init__(self, name, hwgamedevice):
        Observable.__init__(self)
        self._device = hwgamedevice
        self._activated = False
        self._name = name

    def isActivated(self):
        return self._activated

    def getName(self):
        return self._name


class OutGameDevice(GameDevice):

    def set(self, activated):
        if activated:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        self._device.activate(self)
        if self._activated is not True:
            self._activated = True
            Observable.inform(self, self._activated)

    def deactivate(self):
        self._device.deactivate(self)
        if self._activated is not False:
            self._activated = False
            Observable.inform(self, self._activated)


class InGameDevice(GameDevice):

    def __init__(self, name, hwgamedevice, inv=False):
        GameDevice.__init__(self, name, hwgamedevice)
        self._inv = inv

    def inform(self, state):
        if self._inv:
            state = not state

        if self._activated != state:
            self._activated = state
            Observable.inform(self, state)
