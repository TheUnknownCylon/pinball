"""
Simple event based Pinball controller.
Author: TheUC

Known bugs:
* When starting from non-initial state, events might not be excecuted in the
  correct order, resulting in a faulty game state.a

* (Related) In the border case where two related events happen in the same
  game-frame, the game state may get corrupted. (e.g. Flipper button press and
  EOS occur in the same frame, and the EOS event is processed before the
  ENERGIZED event, the game will ignore the first event (not in the correct
  state to process the EOS), next it process the button press, putting the game
  in a state where the game waits for EOS. Since EOS has already been processed
  it will not be re-processed the next game frame.)

Future improvements:

* Formalise serial communication to Arduino (error recovery, 'dirty' start)

"""

from gameengine import GameEngine
from controllerdevices import PowerDriver16, RaspberryPi
from gamedevices import Flipper

from gameengine.sounds import SoundManager
import threading
import time


sm = SoundManager()


class MyPinballGame():

    def __init__(self):

        # Instantiate the hardware
        raspberry = RaspberryPi()
        bank0A = PowerDriver16(0, 0)
        bank0B = PowerDriver16(0, 1)
        devices = [raspberry, bank0A, bank0B]

        flipper_L_POWER_ENERGIZED = bank0B.getOut(0)
        flipper_L_POWER_HOLD = bank0B.getOut(1)
        flipper_L_EOS = raspberry.getIn(17)
        flipper_R_POWER_ENERGIZED = bank0B.getOut(2)
        flipper_R_POWER_HOLD = bank0B.getOut(3)
        flipper_R_EOS = raspberry.getIn(18)
        flipper_L_BUTTON = raspberry.getIn(23)
        flipper_R_BUTTON = raspberry.getIn(24)

        flipperL = Flipper(flipper_L_BUTTON, flipper_L_EOS,
                           flipper_L_POWER_ENERGIZED, flipper_L_POWER_HOLD)
        flipperR = Flipper(flipper_R_BUTTON, flipper_R_EOS,
                           flipper_R_POWER_ENERGIZED, flipper_R_POWER_HOLD)

        ge = GameEngine(devices)

        # Play a sound when the left or right flippers are energized
        flipperL.observe(self, self._flipperEnergized)
        flipperR.observe(self, self._flipperEnergized)
        # self._sFlipper = ge.getSoundManager().createSFX("flipper.wav")

        ge.run()

    def _flipperEnergized(self, state, x):
        # self._sFlipper.play()
        pass

    def testSounds():
        pass


# MyPinballGame()
# sm.playbg("/home/remco/media/main.wav")
# time.sleep(5)

c = TestCinematic()
c.run()

time.sleep(999999)
