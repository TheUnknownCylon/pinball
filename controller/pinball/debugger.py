from __future__ import annotations
from typing import List

import logging
import threading
import tornado.ioloop
import tornado.web
import tornado.websocket

from threading import Timer, Lock
from pinball.hardware.hwdevice import Device

from pinball.gameengine.gameengine import GameEngine
from pinball.hardware.hwdevice import InputDevice, INPUTDEVICECHANGE, OUTPUTDEVICECHANGE

logger = logging.getLogger(__name__)


class DebugEngine():
    def __init__(self, gameengine: GameEngine) -> None:
        self._gameengine = gameengine

    def start(self):
        self._devices = self._gameengine._hwengine.getDevices()
        self._gamelogic = self._gameengine._gamelogic

        guiapp = self.make_gui()
        guiapp.listen(8888)

        t = threading.Thread(target=tornado.ioloop.IOLoop.current().start)
        t.daemon = True
        logger.info("debugger started at http://localhost:8888")
        t.start()

    def make_gui(self):
        return tornado.web.Application(
            [(r"/", PinballPage), (r"/websocket", DebugWebSocket, {
                "devices": self._devices,
                "gameengine": self._gameengine,
                "gamelogic": self._gamelogic,
            })],
            debug=True)


class DebugWebSocket(tornado.websocket.WebSocketHandler):
    """Communication channel with the webpage"""

    def initialize(self, gameengine: GameEngine, devices: List[Device],
                   gamelogic):
        self._fps = FPS(gameengine, self)
        self._devices = devices
        self._gamelogic = gamelogic

    def _deviceupdate(self, d, *args, **kwargs):
        """Sends device status updates to the GUI"""
        try:
            self.write_message("D:{}:{}:{}:{}".format(
                1 if d.isActivated() else 0, id(d), d.getName(),
                isinstance(d, InputDevice)))
        except:
            pass

    def fps(self, fps):
        try:
            self.write_message("FPS:{}".format(fps))
        except:
            pass

    def on_message(self, message):
        (action, hwid) = message.split(":")
        for device in self._devices:
            if id(device) == int(hwid):
                if action == "A":  #activate
                    device._set(True)
                if action == "D":  #deactive
                    device._set(False)

    def open(self):
        logger.debug("WebSocket opened")
        for d in self._devices:
            d.observe(self, INPUTDEVICECHANGE, self._deviceupdate)
            d.observe(self, OUTPUTDEVICECHANGE, self._deviceupdate)
            self._deviceupdate(d)

    def on_close(self):
        logger.debug("WebSocket closed")
        for d in self._devices:
            d.deobserve(self, INPUTDEVICECHANGE, self._deviceupdate)
            d.deobserve(self, OUTPUTDEVICECHANGE, self._deviceupdate)


class PinballPage(tornado.web.RequestHandler):
    """Serves the Pinball GUI page"""

    def get(self):
        self.render("debugger/views/index.html")


class FPS():
    """
    Simple class that can be used to keep track of the games frames per
    second. Each time a game frame is over, the tick() method must be issued.

    The FPS informs its FPS every second to its observers (using the game
    engine internal inform mechanism)
    """

    def __init__(self, gameEngine: GameEngine, debugger: DebugWebSocket):
        self._debugger = debugger
        self._frames = 0
        self._lock = Lock()

        gameEngine.observe(self, GameEngine.TICK, self.tick)

        # Start the FPS thread
        self._printFPS()

    def tick(self, obj, event):
        with self._lock:
            self._frames += 1

    def _printFPS(self):
        t = Timer(1.0, self._printFPS)
        t.setDaemon(True)
        t.start()

        with self._lock:
            self._debugger.fps(self._frames)
            self._frames = 0
