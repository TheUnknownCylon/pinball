from abc import abstractmethod

from typing import List

from pinball.e_observable import Observable
from pinball.controllers.hwgamedevice import GameDevice, OutGameDevice, PwmOutGameDevice


class HWController(Observable):
    """
    Class that can be used by subclasses to represent hardware controllers.
    Hardware controllers are able to 'drive' single hardware devices, such as
    switches, coils, etc.
    """

    def __init__(self):
        Observable.__init__(self)

    @abstractmethod
    def getHwDevices(self) -> List[GameDevice]:
        """
        Returns all known hardware devices for this controller.

        This function should be used for debugging purposes only; for
        interaction with hardware devices use the HWDevice instances directly.

        :return: a list of all registered hardware devices for this controller.
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self):
        """
        Syncs the hardware with the current software state. 

        1. Output devices will get new instructions.
        2. The state of the input devices is read, and new events are triggered
           if there were changes.
        """
        raise NotImplementedError


class BinaryOutHWController(HWController):
    """Base class to indicate that a HWController can control binary out devices."""

    @abstractmethod
    def activate(self, outDevice: OutGameDevice):
        """
        Callback for OutGameDevice to request the controller to activate the
        hardware state for this device. Setting the real hardware state will be
        delayed until sync() is called.

        :param outDevice: the OutGameDevice that has been activated
        """
        raise NotImplementedError

    @abstractmethod
    def deactivate(self, outDevice: OutGameDevice):
        """
        Callback for OutGameDevice to request the controller to deactivate
        the hardware state for this device. Setting the real hardware state
        will be delayed until sync() is called.

        :param outDevice: the OutGameDevice that has been deactivated
        """
        raise NotImplementedError


class PwmOutHWController(HWController):
    """Base class to indicate that a HWController can control instances of :class:`.PwmOutGameDevice`"""

    @abstractmethod
    def update(self, pwmOutDevice: PwmOutGameDevice):
        """
        Callback to indicate that a given pwmOutDevice value has changed and
        the real hardware state needs to be updated. Setting the real hardware 
        state will be delayed until :func:`~PwmOutHWController.sync` is called.

        :param pwmOutDevice: the OutGameDevice that has been deactivated
        """
        raise NotImplementedError
