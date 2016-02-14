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
from controllerdevices import PowerDriver16, RaspberryPi, Mcp23017
from gamedevices import Flipper, Slingshot, Led, GameTimer

devices = set()


def d(device):
    devices.add(device)
    return device

##################################
# Instantiate hardware controllers
raspberry = RaspberryPi()
bank0A = PowerDriver16(0, 0)
bank0B = PowerDriver16(0, 1)
mcp23017 = Mcp23017(0x20)
controllers = [raspberry, bank0A, bank0B, mcp23017]

###################################
# Instantiate devices on controllers
flipper_L_POWER_ENERGIZED = d(bank0B.getOut("L Flipper coil (high)", 0))
flipper_L_POWER_HOLD = d(bank0B.getOut("L Flipper coil (hold)", 1))
flipper_L_EOS = d(raspberry.getIn("L Flipper EOS", -1))
flipper_R_POWER_ENERGIZED = d(bank0B.getOut("R Flipper coil (high)", 2))
flipper_R_POWER_HOLD = d(bank0B.getOut("R Flipper coil (hold)", 3))
flipper_R_EOS = d(raspberry.getIn("R Flipper EOS", -1))
flipper_L_BUTTON = d(raspberry.getIn("L Flipper button", 23))
flipper_R_BUTTON = d(raspberry.getIn("R Flipper button", 24))

slingshot_left_detect = d(mcp23017.getIn("L Slingshot detect", 4, 0))
slingshot_left_coil = d(bank0B.getOut("L Slingshot kicker", 4))
slingshot_right_detect = d(mcp23017.getIn("R Slingshot detect", 3, 0))
slingshot_right_coil = d(bank0B.getOut("R Slingshot kicker", 5))

detect = d(mcp23017.getIn("Switch inline Upper", 6, 0))
detect = d(mcp23017.getIn("Switch inline Lower", 7, 0))

led_1 = Led(d(mcp23017.getOut("Led Blue", 0, 1)))
led_2 = Led(d(mcp23017.getOut("Led Green", 1, 1)))
led_3 = Led(d(mcp23017.getOut("Led Red", 2, 1)))


######################################
# Construct in-game devices using devices on controllers
#  (composed of real-hardware devices)
flipperL = Flipper(flipper_L_BUTTON, flipper_L_EOS,
                   flipper_L_POWER_ENERGIZED, flipper_L_POWER_HOLD)
flipperR = Flipper(flipper_R_BUTTON, flipper_R_EOS,
                   flipper_R_POWER_ENERGIZED, flipper_R_POWER_HOLD)

slingshotL = Slingshot(slingshot_left_detect, slingshot_left_coil)
slingshotR = Slingshot(slingshot_right_detect, slingshot_right_coil)