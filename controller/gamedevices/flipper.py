from .gamedevice import GameDevice
from .timer import GameTimer

BLOCK = 0
UNBLOCK = 0
EOSTIMEOUT = 1


class Flipperstate:
    LOW = "Low"  # 0x00
    ENERGIZED = "Energized"  # 0x01
    HOLD = "Hold"  # 0x02
    EOSHOLD = "EOSHold"  # 0x03
    BLOCKED = "Blocked"  # 0x04
    EOS_ERROR = "EOS ERROR"  # 0xFF


class Flipper(GameDevice):

    """
    Class that manages the state of a single 'fliptronic' flipper.

    When energized, the game waits for the EOS to be triggerd. When this hapens
    the flipper is switched to 'hold' (low current mode) to prevent the flipper
    coil from burning.
    The hardware EOS is backed up by a software EOS: if the hardware EOS is not
    fired within a reasonable amount of time, the flipper is switched to a
    a special hold state. In this special hold state, the flipper can not
    recover from a ball kick: the flipper is down and can not come up again
    without re-pressing the flipper button.
    """

    def __init__(self, button, eos, power_energized, power_hold):
        GameDevice.__init__(self)

        self._state = Flipperstate.LOW
        self._button = button
        self._eos = eos
        self._power_energized = power_energized
        self._power_hold = power_hold
        self._eostimer = GameTimer(0.02)

        button.observe(self, self.flipperEvent)
        eos.observe(self, self.flipperEvent)
        self._eostimer.observe(self, self.flipperEvent)

    def flipperEvent(self, cause, deviceState=None):
        state = self._state
        oldstate = self._state

        if state == Flipperstate.LOW:
            if cause == self._button and deviceState:
                state = Flipperstate.ENERGIZED
            # elif cause == self._eos and deviceState:
                # state = Flipperstate.EOS_ERROR
            elif cause == BLOCK and deviceState:
                state = Flipperstate.BLOCKED

        elif state == Flipperstate.ENERGIZED:
            if cause == self._button and not deviceState:
                state = Flipperstate.LOW
            elif cause == self._eos and deviceState:
                state = Flipperstate.HOLD
            elif cause == self._eostimer:
                print("WARNING: EOS NOT DETECTED, ASSUMING EOS HIGH")
                state = Flipperstate.EOSHOLD

        elif state == Flipperstate.HOLD:
            if cause == self._button and not deviceState:
                state = Flipperstate.LOW
            elif cause == self._eos and not deviceState:
                state = Flipperstate.ENERGIZED

        elif state == Flipperstate.EOSHOLD:
            if cause == self._button and not deviceState:
                state = Flipperstate.LOW
            elif cause == self._eos and deviceState:
                print("(Finally!) GOT EOS")
                state = Flipperstate.HOLD

        elif state == Flipperstate.BLOCKED:
            if cause == UNBLOCK:
                state = Flipperstate.LOW

        if state != oldstate:
            self._state = state
            self._power_energized.set(state == Flipperstate.ENERGIZED)
            self._power_hold.set(
                state == Flipperstate.HOLD or state == Flipperstate.EOSHOLD)
            if state == Flipperstate.ENERGIZED:
                self._eostimer.restart()
            else:
                self._eostimer.cancel()
