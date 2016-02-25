
from .fps import FPS
import e_observable
import time
from debugger.debugger import DebugEngine


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
