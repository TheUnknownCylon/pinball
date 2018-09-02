from __future__ import annotations

import logging
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading

from pinball.hardware.hwdevice import InputDevice

from pinball.gameengine.gameengine import GameEngine

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
                "gamelogic": self._gamelogic,
                "fps": self._gameengine._fps
            })],
            debug=True)


class DebugWebSocket(tornado.websocket.WebSocketHandler):
    """Communication channel with the webpage"""

    def initialize(self, devices, gamelogic, fps):
        self._devices = devices
        self._gamelogic = gamelogic
        fps.observe(self, self._fpsupdate)

    def _deviceupdate(self, d, *args, **kwargs):
        """Sends device status updates to the GUI"""
        try:
            self.write_message("D:{}:{}:{}:{}".format(
                1 if d.isActivated() else 0, id(d), d.getName(),
                isinstance(d, InputDevice)))
        except:
            pass

    def _fpsupdate(self, device):
        try:
            self.write_message("FPS:{}".format(fps._fps))
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
            d.observe(self, self._deviceupdate)
            self._deviceupdate(d)

    def on_close(self):
        logger.debug("WebSocket closed")
        for d in self._devices:
            d.deobserve(self, self._deviceupdate)


class PinballPage(tornado.web.RequestHandler):
    """Serves the Pinball GUI page"""

    def get(self):
        self.render("debugger/views/index.html")
