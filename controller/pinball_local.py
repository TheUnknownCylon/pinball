#!/usr/bin/env python3

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


Construction of a game application:

    1) Instantiate HW Controllers
    2) Instantiate HW Devices
    3) Instantiate GameDevices
    4) Instantiate the GameLogic
    5) Instantiate GameEngine

    A) Run GameEngine
    A1) Point a webbrowser to the debug console (http://hostname:8888)
    B) 'Enjoy' :)

"""

import logging

from pinball.gameengine.gameengine import GameEngine
from pinball.controllers.dummy import DummyController
from pinball.gamedevices.flipper import Flipper
from pinball.gamedevices.led import Led, PwmLed, RGBLed
from pinball.gamedevices.slingshot import Slingshot
from pinball.gamedevices.inlane import Inlane
from gamelogic import MyGame

from pinball.gameengine.sounds import PyGameSoundManager


##################################
# 1) Instantiate hardware controllers
dummyController = DummyController()
controllers = [dummyController]

###################################
# 2) Instantiate devices on controllers
flipper_L_POWER_ENERGIZED = dummyController.getOut("L Flipper coil (high)")
flipper_L_POWER_HOLD = dummyController.getOut("L Flipper coil (hold)")
flipper_L_EOS = dummyController.getIn("L Flipper EOS")
flipper_R_POWER_ENERGIZED = dummyController.getOut("R Flipper coil (high)")
flipper_R_POWER_HOLD = dummyController.getOut("R Flipper coil (hold)")
flipper_R_EOS = dummyController.getIn("R Flipper EOS")
flipper_L_BUTTON = dummyController.getIn("L Flipper button")
flipper_R_BUTTON = dummyController.getIn("R Flipper button")

slingshot_left_detect = dummyController.getIn("L Slingshot detect")
slingshot_left_coil = dummyController.getOut("L Slingshot kicker")
slingshot_right_detect = dummyController.getIn("R Slingshot detect")
slingshot_right_coil = dummyController.getOut("R Slingshot kicker")

inlane_detect_upper = dummyController.getIn("Switch inlane Upper")
inlane_detect_lower = dummyController.getIn("Switch inlane Lower")

led_1 = Led(dummyController.getOut("B-Led Blue"))
led_2 = Led(dummyController.getOut("B-Led Green"))
led_3 = Led(dummyController.getOut("B-Led Red"))

rgbled_1 = dummyController.getPwmOut("RGB-Led Red", (1 << 12) - 1)
rgbled_2 = dummyController.getPwmOut("RGB-Led Green", (1 << 12) - 1)
rgbled_3 = dummyController.getPwmOut("RGB-Led Blue", (1 << 12) - 1)
rgbled = RGBLed(PwmLed(rgbled_1), PwmLed(rgbled_2), PwmLed(rgbled_3))
rgbled.set(0x00ffaf)


######################################
# 3) Instantiate GameDevices -- using devices on controllers
#    (composed of real-hardware devices)
flipperL = Flipper(flipper_L_BUTTON, flipper_L_EOS,
                   flipper_L_POWER_ENERGIZED, flipper_L_POWER_HOLD)
flipperR = Flipper(flipper_R_BUTTON, flipper_R_EOS,
                   flipper_R_POWER_ENERGIZED, flipper_R_POWER_HOLD)

slingshotL = Slingshot(slingshot_left_detect, slingshot_left_coil)
slingshotR = Slingshot(slingshot_right_detect, slingshot_right_coil)

inlane = Inlane(inlane_detect_upper, inlane_detect_lower)

######################################
# 4) Instantiate game logic
#
sm = PyGameSoundManager()
game = MyGame(sm, flipperL, flipperR, slingshotL, slingshotR, inlane, led_1,
              led_2, led_3, rgbled)

# When invoked directly from the CLI, run the pinball engine as main process
if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    ge = GameEngine(controllers, game)
    ge.run()
