import logging
import time
from threading import Timer, Lock

from typing import List

import pinball.e_observable as e_observable

from typing import List
from pinball.hardware.controller import Controller

logger = logging.getLogger(__name__)


class _HardwareEngine():
    def __init__(self, controllers: List[Controller]) -> None:
        self.controllers = controllers

    def tick(self):
        """Advance to the next game frame.
        Syncs all input and output devices with the controller states."""
        for controller in self.controllers:
            controller.sync()

    def getDevices(self):
        """Returns a list of all hardware devices registered to the hardware
        controllers."""
        devices = []
        for controller in self.controllers:
            devices += controller.getDevices()
        return devices


class GameEngine():
    def __init__(self, controllers: List[Controller], gamelogic) -> None:
        # TODO: Type of Gamelogic, and why?
        self._fps = FPS()
        self._hwengine = _HardwareEngine(controllers)
        self._gamelogic = gamelogic

    def run(self):
        e_observable.observerEvents.clear()
        logger.info("game started")

        while True:
            # Improve code here to get a stable FPS
            self.tick()
            time.sleep(1 / 60)
            self._fps.tick()

    def tick(self):
        """Executes the next game logic frame, in the following phases:
        1: Process all events
        2: Sync hardware (input and output)
        """

        while e_observable.observerEvents:
            (event, cause) = e_observable.observerEvents.pop(0)
            event(cause)

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
        self._lock = Lock()

        # Start the FPS thread
        self._printFPS()
        self._fps : int

    def tick(self):
        with self._lock:
            self._frames += 1

    def _printFPS(self):
        t = Timer(1.0, self._printFPS)
        t.setDaemon(True)
        t.start()

        with self._lock:
            self._fps = self._frames
            self._frames = 0
            self.inform()
