
import threading


class FPS:

    """
    Simple class that can be used to keep track of the games frames per
    second. Each time a game frame is over, the tick() method must be issued.
    """

    def __init__(self):
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
            tmp = self._frames
            self._frames = 0
            #print("FPS: {}".format(tmp))
