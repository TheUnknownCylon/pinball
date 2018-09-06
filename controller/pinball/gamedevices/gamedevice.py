from pinball.events import Observable


class GameDevice(Observable):
    """Base class for game devices."""

    def __init__(self):
        Observable.__init__(self)
