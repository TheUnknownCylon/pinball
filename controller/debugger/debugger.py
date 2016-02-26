import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading


class DebugEngine():

    def __init__(self, gameengine):
        self._gameengine = gameengine

    def start(self):
        self._devices = self._gameengine._hwengine.getHwDevices()
        self._gamelogic = self._gameengine._gamelogic

        guiapp = self.make_gui()
        guiapp.listen(8888)

        t = threading.Thread(target=tornado.ioloop.IOLoop.current().start)
        t.daemon = True
        print("DEBUGGER: Started, point your browser to localhost:8888")
        t.start()

    def make_gui(self):
        return tornado.web.Application([
            (r"/", PinballPage),
            (r"/websocket", DebugWebSocket, {
                "devices": self._devices,
                "gamelogic": self._gamelogic,
                "fps": self._gameengine._fps
              })
        ], debug=True)


class DebugWebSocket(tornado.websocket.WebSocketHandler):
    """Communication channel with the webpage"""

    def initialize(self, devices, gamelogic, fps):
        self._devices = devices
        self._gamelogic = gamelogic
        fps.observe(self, self._fpsupdate)

    def _deviceupdate(self, d, *args, **kwargs):
        """Sends device status updates to the GUI"""
        self.write_message("D:{}:{}:{}".format(
            1 if d.isActivated() else 0, id(d), d.getName()))

    def _fpsupdate(self, device, fps):
        self.write_message("FPS:{}".format(fps))

    def open(self):
        print("DEBUGGER: WebSocket opened")
        for d in self._devices:
            d.observe(self, self._deviceupdate)
            self._deviceupdate(d)

    def on_close(self):
        print("DEBUGGER: WebSocket closed")
        for d in self.devices:
            d.deobserve(self, self._deviceupdate)


class PinballPage(tornado.web.RequestHandler):
    """Serves the Pinball GUI page"""

    def get(self):
        self.render("views/index.html")
