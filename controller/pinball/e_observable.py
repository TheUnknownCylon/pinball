from collections import defaultdict

from typing import DefaultDict, List, Tuple, Callable, Any

# Variable that holds all events that need to be processed during the next
# frame
#
# TODO This needs to be refactored. It is a global variable. Perhaps this could
#      be moved to the game-engine?
observerEvents: List[Tuple[Callable, 'Observable', Any]] = []


class Observable:
    """
    Class that represents an event-based observable object. When (an instance)
    of this class wants to inform its observers, it will do not call the
    observers directly. Instead, it stores the inform-request on an event
    queue. Some other game-logic (game engine) can then process the events all
    at once whenever required, allowing a smooth game experience.
    """

    def __init__(self):
        self._observers: DefaultDict[Any, List[Callable]] = defaultdict(list)

    def observe(self, observer: Any, callback: Callable):
        self._observers[observer].append(callback)

    def deobserve(self, observer: Any, callback: Callable):
        try:
            self._observers[observer].remove(callback)
            if len(self._observers[observer]) == 0:
                self._observers.pop(observer, None)
        except:
            pass

    def inform(self):
        """By calling this method, all observers will be informed that there
        has been a change in this observable. This event will be processed
        next tick."""
        for observer in self._observers:
            for callback in self._observers[observer]:
                observerEvents.append((callback, self))
