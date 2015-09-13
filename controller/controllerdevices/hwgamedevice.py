
from e_observable import Observable


class GameDevice(Observable):

    """Data class that represents a device in the game."""

    def __init__(self, bank, pin):
        Observable.__init__(self)
        self._bank = bank
        self._pin = pin


class OutGameDevice(GameDevice):

    def set(self, activated):
        if activated:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        self._bank.activate(self._pin)

    def deactivate(self):
        self._bank.deactivate(self._pin)

    def toggle(self):
        self._bank.toggle(self._pin)


class InGameDevice(GameDevice):
    pass
