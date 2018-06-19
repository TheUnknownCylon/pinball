from pinball.gamedevices.gamedevice import GameDevice


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

    EVENT_INLANESTART = 0
    EVENT_INLANEFAIL = 1
    EVENT_INLANEPASSED = 2
    EVENT_INLANEBACK = 3

    def __init__(self, switch_upper: InGameDevice,
                 switch_lower: InGameDevice) -> None:
        GameDevice.__init__(self)

        self._switch_upper = switch_upper
        self._switch_lower = switch_lower

        self._switch_upper.observe(self, self.detectUpper)
        self._switch_lower.observe(self, self.detectLower)

        self._state = self.NONE

    def reset(self):
        self._state = self.NONE

    def detectLower(self, cause: InGameDevice, deviceState=None):
        """Callback for the inlane lower detection switch."""
        if not deviceState:
            return

        laststate = self._state
        self._state = self.LOWER

        if laststate == self.NONE:
            self._triggerEvent(self.EVENT_INLANESTART)
        elif laststate == self.UPPER:
            self.reset()
        elif laststate == self.LOWER:
            self._triggerEvent(self.EVENT_INLANEFAIL)
            self.reset()

    def detectUpper(self, cause: InGameDevice, deviceState=None):
        """Callback for the inlane upper detection switch."""
        if not deviceState:
            return

        laststate = self._state
        self._state = self.UPPER

        if laststate == self.UPPER:
            self._triggerEvent(self.EVENT_INLANEBACK)
        elif laststate == self.LOWER:
            self._triggerEvent(self.EVENT_INLANEPASSED)

    def registerForInlaneStart(self, observer, callback):
        """Register a callback that is triggered when a ball is fired into
        the inline (from the bottom). This trigger will be followed by a
        inlaneFail trigger or inline passed trigger."""
        self._addObserver(self.EVENT_INLANESTART, observer, callback)

    def registerForInlaneFail(self, observer, callback):
        """Register a callback that is triggered when a ball fails to reach
        the top of the inlane and 'falls back'."""
        self._addObserver(self.EVENT_INLANEFAIL, observer, callback)

    def registerForInlanePassed(self, observer, callback):
        """Register callback that is triggered when a ball has passed the
        inlane and enters the game."""
        self._addObserver(self.EVENT_INLANEPASSED, observer, callback)

    def registerForInlaneBack(self, observer, callback):
        """Register callback that is triggered when a ball that is currently in
        the field returns in the inlane."""
        self._addObserver(self.EVENT_INLANEBACK, observer, callback)
