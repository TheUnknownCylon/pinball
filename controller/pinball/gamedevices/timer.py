import threading

from pinball.e_observable import Observable
from pinball.gamedevices.gamedevice import GameDevice


class GameTimer(GameDevice, Observable):

    """
    Simple timer that can be used in a game. Constructed with a timeout,
    can be started and stopped whenever the game wants to. If a timeout occurs,
    all the observers will be notified. The status argument contains the set
    timeout. When a GameTimer is canceled before the timeout occurs, then
    the observers are not notified.
    """

    def __init__(self, timeout):
        """Constructor, timeout in seconds."""
        GameDevice.__init__(self)
        Observable.__init__(self)
        self._t = None
        self._timeout = timeout

    def restart(self):
        self.cancel()
        self.start()

    def cancel(self):
        if self._t:
            self._t.cancel()
            self._t = None

    def start(self):
        self._t = threading.Timer(self._timeout, self._handle)
        self._t.setDaemon(True)
        self._t.start()

    def _handle(self):
        """Internal handle, informs all observers on the occurence of a
        timeout."""
        self.inform()
