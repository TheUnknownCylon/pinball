from collections import defaultdict


class ObserverRule():

    def __init__(self, observer, callback):
        self.observer = observer
        self.callback = callback


class GameDevice():
    """
    Super class for game devices.
    Contains (protected) functionality for observing functionalities. It is up
    to the device whether the functionalities are used.
    """

    def __init__(self):
        self._observers = defaultdict(list)

    def _addObserver(self, event, observer, callback):
        self._observers[event].append(ObserverRule(observer, callback))

    def _triggerEvent(self, event):
        for observerrule in self._observers[event]:
            observerrule.callback()
