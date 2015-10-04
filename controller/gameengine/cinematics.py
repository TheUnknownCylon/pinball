class TestCinematic():

    def __init__(self):
        self._s1 = sm.createSFX("/home/remco/media/eob_show_1.wav")
        self._s2 = sm.createSFX("/home/remco/media/eob_show_1.wav")
        self._s3 = sm.createSFX("/home/remco/media/eob_show_1.wav")
        self._s4 = sm.createSFX("/home/remco/media/eob_show_4.wav")

        self._parts = [
            (self.partA, 1),
            (self.partB, 1),
            (self.partC, 1),
            (self.partD, 0.5),
            (self.partD, 0.5),
            (self.partD, 0.5)
        ]

    def run(self):
        self._handle(self._parts[:])

    def _handle(self, parts):
        (function, timetonext) = parts.pop(0)
        if parts:
            self._t = threading.Timer(timetonext, self._handle, [parts])
            self._t.setDaemon(True)
            self._t.start()
        function()

    def partA(self):
        print("A")
        self._s1.play()

    def partB(self):
        print("B")
        self._s2.play()

    def partC(self):
        print("C")
        self._s3.play()

    def partD(self):
        print("D")
        self._s4.play()
