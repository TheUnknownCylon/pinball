from time import time

from pinball.gamedevices.gamedevice import GameDevice
from pinball.gamedevices.timer import GameTimer


class Slingshot(GameDevice):

    def __init__(self, detector, coil):
        GameDevice.__init__(self)
        self._coil = coil
        self._coiltimer = GameTimer(0.02)
        self._lastshot = time()

        detector.observe(self, self.slingshotDetect)
        self._coiltimer.observe(self, self.deactivate)

    def slingshotDetect(self, cause, deviceState=None):
        if not deviceState:
            return

        if time() - self._lastshot < 0.2:
            print("> SLINGSHOT Fired again too short after another fire event")
            return

        self._lastshot = time()
        self._coil.set(True)
        self._coiltimer.restart()
        print("> SLINGSHOT FIRE")

    def deactivate(self, cause, deviceState=None):
        self._coil.set(False)
        print("> SLINGSHOT LOW")
