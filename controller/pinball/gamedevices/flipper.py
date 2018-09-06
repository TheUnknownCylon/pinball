import logging

from pinball.hardware.hwdevice import InputDevice, BinaryOutputDevice, INPUTDEVICECHANGE
from pinball.gamedevices.gamedevice import GameDevice
from pinball.gamedevices.timer import GameTimer

logger = logging.getLogger(__name__)


class Flipperstate:
    LOW = "Low"  # 0x00
    ENERGIZED = "Energized"  # 0x01
    HOLD = "Hold"  # 0x02
    EOSHOLD = "EOSHold"  # 0x03
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

    def __init__(self, button: InputDevice, eos: InputDevice,
                 power_energized: BinaryOutputDevice,
                 power_hold: BinaryOutputDevice) -> None:
        GameDevice.__init__(self)

        self._state = Flipperstate.LOW
        self._button = button
        self._eos = eos
        self._power_energized = power_energized
        self._power_hold = power_hold
        self._eostimer = GameTimer(0.02)

        button.observe(self, INPUTDEVICECHANGE, self.flipperEvent)
        eos.observe(self, INPUTDEVICECHANGE, self.flipperEvent)
        self._eostimer.observe(self, GameTimer.TIMER, self.flipperEvent)

    def flipperEvent(self, cause, event):

        state = self._state
        oldstate = self._state

        if state == Flipperstate.LOW:
            if cause == self._button and self._button.isActivated():
                state = Flipperstate.ENERGIZED
            # elif cause == self._eos and deviceState:
            # state = Flipperstate.EOS_ERROR

        elif state == Flipperstate.ENERGIZED:
            if cause == self._button and not self._button.isActivated():
                state = Flipperstate.LOW
            elif cause == self._eos and self._eos.isActivated():
                state = Flipperstate.HOLD
            elif cause == self._eostimer:
                logger.error("eos not detected, assuming eos high")
                state = Flipperstate.EOSHOLD

        elif state == Flipperstate.HOLD:
            if cause == self._button and not self._button.isActivated():
                state = Flipperstate.LOW
            elif cause == self._eos and not self._eos.isActivated():
                state = Flipperstate.ENERGIZED

        elif state == Flipperstate.EOSHOLD:
            if cause == self._button and not self._button.isActivated():
                state = Flipperstate.LOW
            elif cause == self._eos and self._eos.isActivated():
                logger.debug("(finally!) got eos")
                state = Flipperstate.HOLD

        if state != oldstate:
            self._state = state
            self._power_energized.set(state == Flipperstate.ENERGIZED)
            self._power_hold.set(state == Flipperstate.HOLD or state == Flipperstate.EOSHOLD)
            if state == Flipperstate.ENERGIZED:
                self._eostimer.restart()
            else:
                self._eostimer.cancel()
