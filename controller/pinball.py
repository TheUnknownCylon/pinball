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
from pinball.gameengine.audio.dummy import DummySoundManager as SoundManager

from pinball.hardware.dummy import DummyController
from pinball.hardware.powerdriver16 import PowerDriver16
from pinball.hardware.mcp23017 import Mcp23017
from pinball.hardware.tlc4950 import Tlc4950
from pinball.hardware.raspberrypi import RaspberryPi

from pinball.gamedevices.flipper import Flipper
from pinball.gamedevices.inlane import Inlane
from pinball.gamedevices.led import Led, PwmLed, RGBLed
from pinball.gamedevices.slingshot import Slingshot

from pinball.debugger import DebugEngine

from gamelogic import MyGame

##################################
# 1) Instantiate hardware controllers
dummyController = DummyController()
raspberry = RaspberryPi()
powerdriver16 = PowerDriver16("/dev/ttyAMA0")
mcp23017 = Mcp23017(0x20)
tlc4950 = Tlc4950(0x30)
controllers = [dummyController, raspberry, powerdriver16, mcp23017, tlc4950]

###################################
# 2) Instantiate devices on controllers
BANKB = 1
flipper_L_POWER_ENERGIZED = powerdriver16.getOut("L Flipper coil (high)", 0, BANKB, 0)
flipper_L_POWER_HOLD = powerdriver16.getOut("L Flipper coil (hold)", 0, BANKB, 1)
flipper_L_EOS = raspberry.getIn("L Flipper EOS", -1)
flipper_R_POWER_ENERGIZED = powerdriver16.getOut("R Flipper coil (high)", 0, BANKB, 2)
flipper_R_POWER_HOLD = powerdriver16.getOut("R Flipper coil (hold)", 0, BANKB, 3)
flipper_R_EOS = raspberry.getIn("R Flipper EOS", -1)
flipper_L_BUTTON = raspberry.getIn("L Flipper button", 23)
flipper_R_BUTTON = raspberry.getIn("R Flipper button", 24)

slingshot_left_detect = mcp23017.getIn("L Slingshot detect", 2, 1, True)
slingshot_left_coil = powerdriver16.getOut("L Slingshot kicker", 0, BANKB, 4)
slingshot_right_detect = mcp23017.getIn("R Slingshot detect", 3, 1, True)
slingshot_right_coil = powerdriver16.getOut("R Slingshot kicker", 0, BANKB, 5)

inlane_detect_upper = mcp23017.getIn("Switch inlane Upper", 0, 1, True)
inlane_detect_lower = mcp23017.getIn("Switch inlane Lower", 1, 1, True)

balltrough_kicker = dummyController.getOut("Balltrough kicker")
balltrough_led_0 = tlc4950.getPwmOut("Balltrough Led 0", 14)
balltrough_led_1 = tlc4950.getPwmOut("Balltrough Led 1", 13)
balltrough_led_2 = tlc4950.getPwmOut("Balltrough Led 2", 12)
balltrough_led_3 = tlc4950.getPwmOut("Balltrough Led 3", 11)
balltrough_led_4 = tlc4950.getPwmOut("Balltrough Led 4", 10)
balltrough_in_0 = mcp23017.getIn("Balltrough detect 0", 7, 0, True)
balltrough_in_1 = mcp23017.getIn("Balltrough detect 1", 6, 0, True)
balltrough_in_2 = mcp23017.getIn("Balltrough detect 2", 5, 0, True)
balltrough_in_3 = mcp23017.getIn("Balltrough detect 3", 4, 0, True)
balltrough_in_4 = mcp23017.getIn("Balltrough detect 4", 3, 0, True)
#balltrough_opto0 = Opto(PwmLed(balltrough_led_0), balltrough_in_0)
#balltrough_opto1 = Opto(PwmLed(balltrough_led_1), balltrough_in_1)
#balltrough_opto2 = Opto(PwmLed(balltrough_led_2), balltrough_in_2)
#balltrough_opto3 = Opto(PwmLed(balltrough_led_3), balltrough_in_3)
#balltrough_opto4 = Opto(PwmLed(balltrough_led_4), balltrough_in_4)

led_1 = Led(mcp23017.getOut("Led Blue", 0, 1))
led_2 = Led(mcp23017.getOut("Led Green", 1, 1))
led_3 = Led(mcp23017.getOut("Led Red", 2, 1))

rgbled_1 = tlc4950.getPwmOut("RGB-Led Red", 0)
rgbled_2 = tlc4950.getPwmOut("RGB-Led Green", 1)
rgbled_3 = tlc4950.getPwmOut("RGB-Led Blue", 2)
rgbled = RGBLed(PwmLed(rgbled_1), PwmLed(rgbled_2), PwmLed(rgbled_3))
rgbled.set(0x00ffaf)

######################################
# 3) Instantiate GameDevices -- using devices on controllers
#    (composed of real-hardware devices)
flipperL = Flipper(flipper_L_BUTTON, flipper_L_EOS,
                   flipper_L_POWER_ENERGIZED, flipper_L_POWER_HOLD)
flipperR = Flipper(flipper_R_BUTTON, flipper_R_EOS,
                   flipper_R_POWER_ENERGIZED, flipper_R_POWER_HOLD)

#balltrough = Balltrough(balltrough_kicker, [
#    balltrough_opto0,
#    balltrough_opto1,
#     balltrough_opto2,
#     balltrough_opto3,
#     balltrough_opto4,
#])

slingshotL = Slingshot(slingshot_left_detect, slingshot_left_coil)
slingshotR = Slingshot(slingshot_right_detect, slingshot_right_coil)

inlane = Inlane(inlane_detect_upper, inlane_detect_lower)

######################################
# 4) Instantiate game logic
#
sm = SoundManager()
game = MyGame(sm, flipperL, flipperR, slingshotL, slingshotR, inlane)

# When invoked directly from the CLI, run the pinball engine as main process
if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    ge = GameEngine(controllers, game)
    debugger = DebugEngine(ge)
    debugger.start()
    ge.run()
