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

from pinball.gameengine import GameEngine
from pinball.controllers.powerdriver16 import PowerDriver16
from pinball.controllers.mcp23017 import Mcp23017
from pinball.controllers.raspberrypi import RaspberryPi
from pinball.gamedevices.flipper import Flipper
from pinball.gamedevices.slingshot import Slingshot
from pinball.gamedevices.led import Led
from pinball.gamedevices.inlane import Inlane

from gamelogic import MyGame

##################################
# 1) Instantiate hardware controllers
raspberry = RaspberryPi()
powerdriver16 = PowerDriver16("/dev/ttyAMA0")
mcp23017 = Mcp23017(0x20)
controllers = [raspberry, powerdriver16, mcp23017]

###################################
# 2) Instantiate devices on controllers
flipper_L_POWER_ENERGIZED = powerdriver16.getOut("L Flipper coil (high)", 0, BANKB, 0)
flipper_L_POWER_HOLD = powerdriver16.getOut("L Flipper coil (hold)", 0, BANKB, 1)
flipper_L_EOS = raspberry.getIn("L Flipper EOS", -1)
flipper_R_POWER_ENERGIZED = powerdriver16.getOut("R Flipper coil (high)", 0, BANKB, 2)
flipper_R_POWER_HOLD = powerdriver16.getOut("R Flipper coil (hold)", 0, BANKB, 3)
flipper_R_EOS = raspberry.getIn("R Flipper EOS", -1)
flipper_L_BUTTON = raspberry.getIn("L Flipper button", 23)
flipper_R_BUTTON = raspberry.getIn("R Flipper button", 24)

slingshot_left_detect = mcp23017.getIn("L Slingshot detect", 3, 0)
slingshot_left_coil = powerdriver16.getOut("L Slingshot kicker", 0, BANKB, 4)
slingshot_right_detect = mcp23017.getIn("R Slingshot detect", 4, 0)
slingshot_right_coil = powerdriver16.getOut("R Slingshot kicker", 0, BANKB, 5)

inlane_detect_upper = mcp23017.getIn("Switch inlane Upper", 6, 0, inv=True)
inlane_detect_lower = mcp23017.getIn("Switch inlane Lower", 5, 0, inv=True)

led_1 = Led(mcp23017.getOut("Led Blue", 0, 1))
led_2 = Led(mcp23017.getOut("Led Green", 1, 1))
led_3 = Led(mcp23017.getOut("Led Red", 2, 1))


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
game = MyGame(flipperL, flipperR, slingshotL, slingshotR, inlane, led_1,
              led_2, led_3)

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
