import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading

from pinball import *


class PBWebSocket(tornado.websocket.WebSocketHandler):

    def _deviceupdate(self, d, *args, **kwargs):
        """Sends device status updates to the GUI"""
        self.write_message("D:{}:{}:{}".format(
            1 if d.isActivated() else 0, id(d), d.getName()))

    """Communication channel with the webpage"""

    def open(self):
        print("WebSocket opened")
        for d in devices:
            d.observe(self, self._deviceupdate)
            self._deviceupdate(d)

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
        print("WebSocket closed")
        for d in devices:
            d.deobserve(self, self._deviceupdate)


class PinballPage(tornado.web.RequestHandler):
    """Serves the Pinball GUI page"""

    def get(self):
        self.render("views/index.html")


def make_gui():
    return tornado.web.Application([
        (r"/", PinballPage),
        (r"/websocket", PBWebSocket)
    ], debug=True)

    # Start the pinball machine and GUI when started from the CLI
if __name__ == "__main__":
    ge = GameEngine(controllers)
    t = threading.Thread(target=ge.run)
    t.daemon = True
    t.start()

    guiapp = make_gui()
    guiapp.listen(8888)
    tornado.ioloop.IOLoop.current().start()
