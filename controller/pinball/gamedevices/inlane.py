from pinball.gamedevices.gamedevice import GameDevice

from pinball.hardware.hwdevice import InputDevice, INPUTDEVICECHANGE
from pinball.events import EventType


class Inlane(GameDevice):
    """
    Represents a simple inlane implementation, where the inlane consists of
    a single lower detection switch, and a single upper detection switch.

    Provides callbacks for ball passing through the inlane, pass returning into
    the inlane.

    Current limitations:
        - Supports only a single ball in the game.

        - When launching, if the ball returns WHILE hitting a switch, the game
          can not properly detect the return and the inlane goes into an
          incorrect state.
    """

    NONE = 0  # State: No ball has entered the inlane (no ball in-game)
    LOWER = 1  # State: last switch activated was the lower switch
    UPPER = 2  # State: last switch activated was the upper switch

    EVENT_INLANESTART = EventType()
    EVENT_INLANEFAIL = EventType()
    EVENT_INLANEPASSED = EventType()
    EVENT_INLANEBACK = EventType()

    def __init__(self, switch_upper: InputDevice,
                 switch_lower: InputDevice) -> None:
        GameDevice.__init__(self)

        self._switch_upper = switch_upper
        self._switch_lower = switch_lower

        self._switch_upper.observe(INPUTDEVICECHANGE, self.detectUpper)
        self._switch_lower.observe(INPUTDEVICECHANGE, self.detectLower)

        self._state = self.NONE

    def reset(self):
        self._state = self.NONE

    def detectLower(self, cause, eventType):
        """Callback for the inlane lower detection switch."""
        deviceState = cause.isActivated()
        if not deviceState:
            return

        laststate = self._state
        self._state = self.LOWER

        if laststate == self.NONE:
            self.signal(Inlane.EVENT_INLANESTART)
        elif laststate == self.UPPER:
            self.reset()
        elif laststate == self.LOWER:
            self.signal(Inlane.EVENT_INLANEFAIL)
            self.reset()

    def detectUpper(self, cause, eventType):
        """Callback for the inlane upper detection switch."""
        deviceState = cause.isActivated()
        if not deviceState:
            return

        laststate = self._state
        self._state = self.UPPER

        if laststate == self.UPPER:
            self.signal(Inlane.EVENT_INLANEBACK)
        elif laststate == self.LOWER:
            self.signal(Inlane.EVENT_INLANEPASSED)
