from threading import Timer


class ShowScript():
    def __init__(self):
        self._parts = []

    def add(self, action, delay):
        self._parts.append((action, delay))
        return self

    def start(self, loop=False):
        show = Show(self._parts, loop)
        show.start()
        return show


class Show():

    def __init__(self, script, loop):
        self._running = False
        self._script = script
        self._loop = loop

    def start(self):
        if self._running:
            return

        self._running = True
        self._scheduleStep(0)

    def _scheduleStep(self, line):
        (action, delay) = self._script[line]
        t = Timer(delay, self._runStep, [line])
        t.setDaemon(True)
        t.start()

    def _runStep(self, line):
        # Abort if we have been stopped during the wait
        if not self._running:
            return

        (action, delay) = self._script[line]
        if self._loop or line < len(self._script) - 1:
            self._scheduleStep((line + 1) % len(self._script))
        action()

    def stop(self):
        self._running = False
