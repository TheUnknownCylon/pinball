import threading
from e_observable import Observable


class FPS(Observable):

    """
    Simple class that can be used to keep track of the games frames per
    second. Each time a game frame is over, the tick() method must be issued.

    The FPS informs its FPS every second to its observers (using the game
    engine internal inform mechanism)
    """

    def __init__(self):
        Observable.__init__(self)
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
