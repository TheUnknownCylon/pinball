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
from gamedevices import Flipper, Slingshot

# Instantiate the hardware
raspberry = RaspberryPi()
bank0A = PowerDriver16(0, 0)
bank0B = PowerDriver16(0, 1)
devices = [raspberry, bank0A, bank0B]

flipper_L_POWER_ENERGIZED = bank0B.getOut(0)
flipper_L_POWER_HOLD = bank0B.getOut(1)
flipper_L_EOS = raspberry.getIn(-1)
flipper_R_POWER_ENERGIZED = bank0B.getOut(2)
flipper_R_POWER_HOLD = bank0B.getOut(3)
flipper_R_EOS = raspberry.getIn(-1)
flipper_L_BUTTON = raspberry.getIn(23)
flipper_R_BUTTON = raspberry.getIn(24)

slingshot_left_detect = raspberry.getIn(18)
slingshot_left_coil = bank0B.getOut(4)
slingshot_right_detect = raspberry.getIn(22)
slingshot_right_coil = bank0B.getOut(5)

flipperL = Flipper(flipper_L_BUTTON, flipper_L_EOS,
        flipper_L_POWER_ENERGIZED, flipper_L_POWER_HOLD)
flipperR = Flipper(flipper_R_BUTTON, flipper_R_EOS,
        flipper_R_POWER_ENERGIZED, flipper_R_POWER_HOLD)

slingshotL = Slingshot(slingshot_left_detect, slingshot_left_coil)
slingshotR = Slingshot(slingshot_right_detect, slingshot_right_coil)


#######################################
# All code below is *experimental* flipper control over curses
# It doesn't work very well... 
# * curses does not support, so no two flippers at the same time
# * holding a key down results in KEYPRESS <LONG WAIT> KEYPRESS <SHORT WAIT> KEYPRESS <SHORT WAIT> (...)
#   (as in typing text in a terminal)
#
import threading
import curses
from curses import wrapper
import time
from gamedevices import GameTimer
ge = GameEngine(devices)
t = threading.Thread(target=ge.run)
t.daemon = True
t.start()

def deactL(*args, **kwargs):
    flipper_L_BUTTON.inform(False)
def deactR(*args, **kwargs):
    flipper_R_BUTTON.inform(False)

def pinballui(stdscr):

    stdscr.clear()
    stdscr.nodelay(True)

    tL = GameTimer(0.7)
    tR = GameTimer(0.7)
    tL.observe("m", deactL)
    tR.observe("m", deactR)


    while True:
        c = stdscr.getch()
        nleft = c == curses.KEY_SLEFT or c == ord('z')
        nright = c == curses.KEY_SRIGHT or c == ord('x')

        if nleft:
            flipper_L_BUTTON.inform(True)
            tL.restart()

        if nright:
            flipper_R_BUTTON.inform(True)
            tR.restart()

        time.sleep(0.01)

wrapper(pinballui)
