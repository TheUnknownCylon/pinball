from .gamedevice import GameDevice
from .timer import GameTimer
from time import time


class Slingshot(GameDevice):

    def __init__(self, detector, coil):
        GameDevice.__init__(self)
        self._detector = detector
        self._coil = coil
        self._coiltimer = GameTimer(0.02)
        self._lastshot = time()

        detector.observe(self, self.slingshotDetect)
        self._coiltimer.observe(self, self.deactivate)

    def slingshotDetect(self, cause, deviceState=None):
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
