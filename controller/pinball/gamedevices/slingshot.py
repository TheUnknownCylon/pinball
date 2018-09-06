import logging
from time import time

from pinball.gamedevices.gamedevice import GameDevice
from pinball.gamedevices.timer import GameTimer

from pinball.hardware.hwdevice import InputDevice, INPUTDEVICECHANGE
from pinball.hardware.hwdevice import BinaryOutputDevice

logger = logging.getLogger(__name__)


class Slingshot(GameDevice):

    def __init__(self, detector: InputDevice, coil: BinaryOutputDevice) -> None:
        GameDevice.__init__(self)
        self._coil = coil
        self._coiltimer = GameTimer(0.02)
        self._lastshot = time()

        detector.observe(INPUTDEVICECHANGE, self.slingshotDetect)
        self._coiltimer.observe(GameTimer.TIMER, self.deactivate)

    def slingshotDetect(self, detector, eventtype):
        if not detector.isActivated():
            return

        if time() - self._lastshot < 0.2:
            # debounce
            logging.info("slingshot fired again too short after another fire event")
            return

        self._lastshot = time()
        self._coil.set(True)
        self._coiltimer.restart()
        logging.info("slingshot fire")

    def deactivate(self, detector, eventtype):
        self._coil.set(False)
        logging.info("slingshot low")
