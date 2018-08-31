from __future__ import annotations

from pinball.e_observable import Observable
from pinball.controllers.hwcontroller import OutputHWController


class Device(Observable):
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


class InputDevice(Device):
    """
    Represents a digital input game device.
    It can have two states: activate (on) or not active (off).
    """

    def __init__(self, name) -> None:
        Device.__init__(self, name)
        self._activated = False

    def _set(self, activated: bool):
        """
        Method to be called by the :class:`HWController` when the controller reads a new
        state of this device.
        
        :param activated: True if the new state is activated, False if the new state is deactivated. 
        """
        if self._activated != activated:
            self._activated = activated
            Observable.inform(self)


class OutputDevice(Device):
    """Represents an output device"""

    def __init__(self, name):
        Device.__init__(self, name)

    def activate(self):
        """Activates the hardware device."""
        raise NotImplementedError

    def deactivate(self):
        """Activates the hardware device."""
        raise NotImplementedError


class BinaryOutputDevice(OutputDevice):
    """
    Represents a digital output game device.
    It can have two states: activate (on) or not active (off).
    """

    def __init__(self, name, hwController: OutputHWController) -> None:
        OutputDevice.__init__(self, name)
        self._hwController = hwController
        self._activated = False

    def set(self, activated: bool):
        """
        Activates or deactives the given device. Note that the actual device
        activation or deactivation is delayed until the controllers sync is
        being called.

        :param activated: boolean to indicate activation or deactivation
        """
        if self._activated != activated:
            self._activated = activated
            self._hwController.update(self)

    def get(self) -> bool:
        """
        :return: true if the device is activated after the next controller sync
        """
        return self._activated

    def activate(self):
        """Activates the hardware device."""
        self.set(True)

    def deactivate(self):
        """Deactivates the hardware device."""
        self.set(False)


class PwmOutputDevice(OutputDevice):
    def __init__(self, name, hwController: OutputHWController,
                 maxIntensity: int) -> None:
        """
        Constructs a new output device that can be controlled using PWM.

        :param name: human-readable name of this device
        :param hwController: the controller that manages this device
        :param maxIntensity: maximum intensity value that can be set
        """
        OutputDevice.__init__(self, name)
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

    def maxIntensity(self) -> int:
        """Returns the maximum intensity value of this device."""
        return self._maxIntensity

