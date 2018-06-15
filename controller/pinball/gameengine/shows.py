from threading import Timer


class ShowScript():
    def __init__(self):
        self._parts = []

    def add(self, action, delay=0):
        self._parts.append((action, delay))
        return self

    def start(self, loop=False):
        show = Show(self._script(loop))
        show.start()
        return show

    def _script(self, loop=False):
        while True:
            script = self._parts[:]
            for line in script:
                yield line

            if not loop:
                break


class Show():

    def __init__(self, script):
        self._running = False
        self._script = script

    def start(self):
        if self._running:
            return

        self._running = True
        self._scheduleStep(None)

    def _scheduleStep(self, action):
        if not self._running:
            return

        try:
            (nextAction, delay) = next(self._script)
            t = Timer(delay, self._scheduleStep, [nextAction])
            t.setDaemon(True)
            t.start()
        except StopIteration:
            pass

        if action:
            action()

    def stop(self):
        self._running = False
