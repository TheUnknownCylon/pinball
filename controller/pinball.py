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
import threading

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


##############################################################################
# Code that provides a (web) GUI for the pinball machine
import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket

class PBWebSocket(tornado.websocket.WebSocketHandler):
    """Communication channel with the webpage"""
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        if message == "LD":
            flipper_L_BUTTON.inform(True)
        elif message == "LU":
            flipper_L_BUTTON.inform(False)
        elif message == "RD":
            flipper_R_BUTTON.inform(True)
        elif message == "RU":
            flipper_R_BUTTON.inform(False)

    def on_close(self):
        print("WebSocket closed");


class PinballPage(tornado.web.RequestHandler):
    """Serves the Pinball GUI page"""
    def get(self):
        self.render("views/index.html")

def make_gui():
    return tornado.web.Application([
        (r"/", PinballPage),
        (r"/websocket", PBWebSocket),
        ])

# Start the pinball machine and GUI when started from the CLI
if __name__ == "__main__":
    ge = GameEngine(devices)
    t = threading.Thread(target=ge.run)
    t.daemon = True
    t.start()

    guiapp = make_gui()
    guiapp.listen(8888)
    tornado.ioloop.IOLoop.current().start()

