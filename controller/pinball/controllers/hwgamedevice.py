from pinball.e_observable import Observable


class GameDevice(Observable):

    """Data class that represents a two-state hardware device in the game."""

    def __init__(self, name):
        Observable.__init__(self)
        self._activated = False
        self._name = name

    def isActivated(self):
        return self._activated

    def getName(self):
        return self._name

    def __str__(self):
        return "{}:{}".format(type(self).__name__, self._name)


class InGameDevice(GameDevice):
    """
    Represents a digital input game device.
    It can have two states: activate (on) or not active (off).
    """

    def __init__(self, name, inv=False):
        GameDevice.__init__(self, name)
        self._inv = inv

    def inform(self, state):
        if self._inv:
            state = not state

        if self._activated != state:
            self._activated = state
            Observable.inform(self, state)


class OutGameDevice(GameDevice):
    """
    Represents a digital output game device.
    It can have two states: activate (on) or not active (off).
    """

    def __init__(self, name, binaryOutHWController):
        GameDevice.__init__(self, name)
        self._hwController = binaryOutHWController

    def set(self, activated):
        if activated:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        self._hwController.activate(self)
        if self._activated is not True:
            self._activated = True
            Observable.inform(self, self._activated)

    def deactivate(self):
        self._hwController.deactivate(self)
        if self._activated is not False:
            self._activated = False
            Observable.inform(self, self._activated)


class PwmOutGameDevice(GameDevice):

    def __init__(self, name, hwController, maxIntensity):
        GameDevice.__init__(self, name)
        self._hwController = hwController
        self._maxIntensity = maxIntensity
        self._intensity = 0

    def setIntensity(self, value):
        if value > self._maxIntensity:
            value = self._maxIntensity
        elif value < 0:
            value = 0
        self._intensity = value
        self._activated = value > 0

        self._hwController.update(self)
        Observable.inform(self, self._activated)

    def maxIntensity(self):
        return self._maxIntensity
