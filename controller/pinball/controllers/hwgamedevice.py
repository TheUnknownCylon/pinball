from pinball.e_observable import Observable


class GameDevice(Observable):
    """Data class that represents a hardware device, such as a coil, switch, or LED."""

    def __init__(self, name):
        """
        Constructs a new representation of a hardware game device.

        :param name: Human readable name of the device.
        """
        Observable.__init__(self)
        self._activated = False
        self._name = name

    def isActivated(self) -> bool:
        """
        Method to check whether the device is activated.

        :return: true if activated, false otherwise
        """
        return self._activated

    def getName(self):
        """
        :return: the name of this device
        """
        return self._name

    def __str__(self) -> str:
        return "{}:{}".format(type(self).__name__, self._name)


class InGameDevice(GameDevice):
    """
    Represents a digital input game device.
    It can have two states: activate (on) or not active (off).
    """

    def __init__(self, name, inv: bool = False) -> None:
        GameDevice.__init__(self, name)
        self._inv = inv

    def inform(self, state: bool):
        """
        Method to set the new state of this device.
        
        Informs all observers that the state of this device has changed.
        
        :param state: True if the new state is activated, False if the new state is deactivated. 
        """
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

    def __init__(self, name,
                 binaryOutHWController: 'BinaryOutHWController') -> None:
        GameDevice.__init__(self, name)
        self._hwController = binaryOutHWController

    def set(self, activated: bool):
        """
        Activates or deactives the given device.

        :param activated: boolean to indicate activation or deactivation
        """
        if activated:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        """Activates the hardware device."""
        self._hwController.activate(self)
        if self._activated is not True:
            self._activated = True
            Observable.inform(self, self._activated)

    def deactivate(self):
        """Deactivates the hardware device."""
        self._hwController.deactivate(self)
        if self._activated is not False:
            self._activated = False
            Observable.inform(self, self._activated)


class PwmOutGameDevice(GameDevice):
    def __init__(self, name, hwController: 'PwmOutHWController',
                 maxIntensity: int) -> None:
        """
        Constructs a new PwmOutGameDevice.

        :param name: human-readable name of this device
        :param hwController: the controller that manages this device
        :param maxIntensity: maximum intensity value that can be set
        """
        GameDevice.__init__(self, name)
        self._hwController = hwController
        self._maxIntensity = maxIntensity
        self._intensity = 0
        self._lastActive = self._intensity

    def activate(self):
        """Activates the hardware device, the previous intensity value will be set."""
        value = self._lastActive if self._lastActive else self._maxIntensity
        self.setIntensity(value)

    def deactivate(self):
        """Deactives the hardware device."""
        self.setIntensity(0x00)

    def setIntensity(self, value: int):
        """
        Sets the intensity of the device.

        If the device is deactived, it will be activated.
        
        If value is lower or equal to 0 is passed, then the device is deactived.
        If value is larger than the maximum intensity, then the device intensity is set to its max value. 

        :param value: the new intensity value
        """
        if value > self._maxIntensity:
            value = self._maxIntensity
        elif value < 0:
            value = 0

        if value:
            self._lastActive = value

        self._intensity = value
        self._activated = value > 0

        self._hwController.update(self)
        Observable.inform(self, self._activated)

    def maxIntensity(self) -> int:
        """Returns the maximum intensity value of this device."""
        return self._maxIntensity


# Imports for type checks only (circular dependency)
from pinball.controllers.hwcontroller import HWController, BinaryOutHWController, PwmOutHWController
