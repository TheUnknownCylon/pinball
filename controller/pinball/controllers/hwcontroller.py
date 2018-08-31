from __future__ import annotations

from abc import abstractmethod

from typing import List

from pinball.e_observable import Observable


class HWController(Observable):
    """
    Class that can be used by subclasses to represent hardware controllers.

    Hardware controllers are able to 'drive' individual hardware devices, such 
    as switches, coils, etc.
    """

    def __init__(self):
        Observable.__init__(self)

    @abstractmethod
    def getDevices(self) -> List[Device]:
        """
        Returns all known devices for this controller.

        This function should be used for debugging purposes only; for
        interaction with hardware devices use the HWDevice instances directly.

        :return: a list of all registered hardware devices for this controller.
        """
        raise NotImplementedError

    @abstractmethod
    def sync(self):
        """
        This method is being called when the hardware state should be synced 
        with the software state. For output devices this means that the 
        controller updates the state of the device. For input devices this
        means that the device state is read, and corresponding events will be
        triggered.
        """
        raise NotImplementedError


class OutputHWController(HWController):
    """
    Base class for controllers which control instances of :class:`OutputDevice`.

    This class is not intended to be used outside this package.  
    """

    @abstractmethod
    def update(self, outDevice: OutputDevice):
        """
        Callback for :class:`OutputDevice` to inform the controller that the
        state of the device should be changed during the next 
        :func:`~HWController.sync`.

        :param outDevice: the OutGameDevice that has been activated
        """
        raise NotImplementedError


from pinball.controllers.hwdevice import Device, OutputDevice
