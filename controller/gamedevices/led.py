
class Led():

    """Represents a single color LED device. The LED can be turned on or off.
    """

    def __init__(self, led):
        self._led = led

    def on(self):
        self._led.activate()

    def off(self):
        self._led.deactivate()
