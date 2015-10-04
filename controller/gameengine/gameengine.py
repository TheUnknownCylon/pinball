
from .fps import FPS
from .sounds import SoundManager
import e_observable
import time


class GameEngine():

    def __init__(self, gameControllerDevices=None):
        self._fps = FPS()
        self._soundmanager = SoundManager()

        self._devices = set()
        for dv in gameControllerDevices:
            self._devices.add(dv)

    def addGameControllerDevice(self, device):
        self._devices.add(device)

    def getSoundManager(self):
        """Returns a sound manager that can be used to play game sounds"""
        return self._soundmanager

    def _tick(self):
        """Executes the game logic"""
        while e_observable.observerEvents:
            (event, cause, newstate) = e_observable.observerEvents.pop(0)
            event(cause, newstate)

    def _sync(self):
        """Updates the software <--> hardware state of all hardware devices"""
        for device in self._devices:
            device.sync()

    def run(self):
        while True:
            self._tick()

            self._sync()
            # TODO: Two pass sync? Write to devices before going to
            #      sleep, and read from devices after sleep.
            #
            #      Not implemented yet:
            #      When the sleep timer is very low, no one will
            #      ever notice the difference.

            time.sleep(0.002)
            self._fps._tick()
