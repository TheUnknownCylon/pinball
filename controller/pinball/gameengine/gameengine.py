import logging
from typing import List

import time
import pinball.events

from pinball.events import Observable, EventType
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


class GameEngine(Observable):
    TICK = EventType()

    def __init__(self, controllers: List[Controller], gamelogic) -> None:
        Observable.__init__(self)
        self._hwengine = _HardwareEngine(controllers)
        self._gamelogic = gamelogic

    def run(self):
        logger.info("game started")

        while True:
            # Improve code here to get a stable FPS
            self.signal(GameEngine.TICK)
            pinball.events.process()
            self._hwengine.tick()
            time.sleep(1 / 60)
            pinball.events.process()
