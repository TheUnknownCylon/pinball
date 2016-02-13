
from e_observable import Observable


class HWController(Observable):

    def __init__(self):
        Observable.__init__(self)

    def sync(self):
        """ Syncs the hardware with the current software state.
        1. Output devices will get new instructions.
        2. The state of the input devices is read, and new events are triggered
           if there were changes."""
        raise NotImlemented()

    def activate(self, outDevice):
        """ Callback for OutGameDevice to request the controller to activate the
        hardware state for this device. Setting the real hardware state will be
        delayed until sync() is called."""
        raise NotImlemented()

    def deactivate(self, outDevice):
        """ Callback for OutGameDevice to request the controller to deactivate
        the hardware state for this device. Setting the real hardware state
        will be delayed until sync() is called."""
        raise NotImlemented()
