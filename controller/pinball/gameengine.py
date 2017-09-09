import time
import threading

import pinball.e_observable as e_observable
from pinball.debugger import DebugEngine


class HardwareEngine():

    def __init__(self, hwcontrollers):
        self.hwcontrollers = hwcontrollers

    def tick(self):
        """Advance to the next game frame.
        Syncs all input and output devices with the controller states."""
        for controller in self.hwcontrollers:
            controller.sync()

    def getHwDevices(self):
        """Returns a list of all hardware devices registered to the hardware
        controllers."""
        devices = []
        for controller in self.hwcontrollers:
            devices += controller.getHwDevices()
        return devices


class GameEngine():

    def __init__(self, hwcontrollers, gamelogic):
        self._fps = FPS()
        self._hwengine = HardwareEngine(hwcontrollers)
        self._gamelogic = gamelogic
        self._debugger = DebugEngine(self)

    def run(self):
        self._debugger.start()
        e_observable.observerEvents.clear()
        print("STARTING THE GAME")

        while True:
            self.tick()
            time.sleep(0.002)
            self._fps.tick()

    def tick(self):
        """Executes the next game logic frame, in the following phases:
        1: Process all events
        2: Sync hardware (input and output)
        """

        while e_observable.observerEvents:
            (event, cause, newstate) = e_observable.observerEvents.pop(0)
            event(cause, newstate)

        # TODO: Two pass sync? Write to devices before going to
        #      sleep, and read from devices after sleep.
        #
        #      Not implemented yet:
        #      When the sleep timer is very low, no one will
        #      ever notice the difference.
        self._hwengine.tick()


class FPS(e_observable.Observable):

    """
    Simple class that can be used to keep track of the games frames per
    second. Each time a game frame is over, the tick() method must be issued.

    The FPS informs its FPS every second to its observers (using the game
    engine internal inform mechanism)
    """

    def __init__(self):
        e_observable.Observable.__init__(self)
        self._frames = 0
        self._lock = threading.Lock()

        # Start the FPS thread
        self._printFPS()

    def tick(self):
        with self._lock:
            self._frames += 1

    def _printFPS(self):
        t = threading.Timer(1.0, self._printFPS)
        t.setDaemon(True)
        t.start()
        global frames
        with self._lock:
            fps = self._frames
            self._frames = 0
            self.inform(fps)
