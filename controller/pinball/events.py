from __future__ import annotations
from typing import DefaultDict, List, Tuple, Callable, Any

from collections import defaultdict

__observerEvents__: List[ObserverEvent] = []


class EventType():
    pass


class Observable:
    """
    Class that represents an event-based observable object. When (an instance)
    of this class wants to inform its observers, it will do not call the
    observers directly. Instead, it stores the inform-request on an event
    queue. Some other game-logic (game engine) can then process the events all
    at once whenever required, allowing a smooth game experience.
    """

    def __init__(self) -> None:
        self._observers: DefaultDict[EventType, List[
            ObserverRule]] = defaultdict(list)

    def observe(self, observer: Any, eventType: EventType, callback: Callable):
        self._observers[eventType].append(
            ObserverRule(observer, eventType, callback))

    def deobserve(self, observer: Any, eventType: EventType,
                  callback: Callable):
        self._observers[eventType] = [
            rule for rule in self._observers[eventType]
            if rule.observer is not observer and rule.callback is not callback
        ]

    def signal(self, eventType: EventType):
        """
        By calling this method, all observers will be informed that there
        has been a change in this observable. This event will be processed
        next tick.
        """
        global __observerEvents__
        for rule in self._observers[eventType]:
            __observerEvents__.append(ObserverEvent(self, rule))


class ObserverEvent():
    def __init__(self, observable: Observable, rule: ObserverRule) -> None:
        self._observable = observable
        self._rule = rule

    def fire(self):
        self._rule.callback(self._observable, self._rule.eventType)


class ObserverRule():
    def __init__(self, observer: Any, eventType: EventType,
                 callback: Callable) -> None:
        self.observer = observer
        self.eventType = eventType
        self.callback = callback


def process():
    global __observerEvents__
    events = __observerEvents__
    __observerEvents__ = []
    for event in events:
        event.fire()
