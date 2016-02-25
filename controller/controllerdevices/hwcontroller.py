
from e_observable import Observable


class HWController(Observable):
    """Class that can be used by subclasses to represent hardware controllers.
    Hardware controllers are able to 'drive' single hardware devices, such as
    switches, coils, etc."""

    def __init__(self):
        Observable.__init__(self)

    def getHwDevices(self):
        """Returns a list of all registered hardware devices.

        This function should be used for debugging purposes only; for
        interaction with hardware devices use the HWDevice instances directly.
        """
        raise NotImplementedError

    def sync(self):
        """ Syncs the hardware with the current software state.
        1. Output devices will get new instructions.
        2. The state of the input devices is read, and new events are triggered
           if there were changes."""
        raise NotImplementedError

    def activate(self, outDevice):
        """ Callback for OutGameDevice to request the controller to activate the
        hardware state for this device. Setting the real hardware state will be
        delayed until sync() is called."""
        raise NotImplementedError

    def deactivate(self, outDevice):
        """ Callback for OutGameDevice to request the controller to deactivate
        the hardware state for this device. Setting the real hardware state
        will be delayed until sync() is called."""
        raise NotImplementedError
