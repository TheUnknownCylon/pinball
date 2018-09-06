import logging
from pinball.gamedevices.flipper import Flipper
from pinball.gamedevices.inlane import Inlane
from pinball.gamedevices.led import Led, PwmLed, RGBLed
from pinball.gamedevices.slingshot import Slingshot
from pinball.gameengine.audio import AbstractSoundManager

from pinball.gameengine.shows import ShowScript

logger = logging.getLogger(__name__)

dir = "/home/remco/pinball/soundsamples/"
dir = "/home/remco/media/"


class MyGame():
    def __init__(self, sm: AbstractSoundManager, flipper_l: Flipper,
                 flipper_r: Flipper, slingshot_l: Slingshot,
                 slingshot_r: Slingshot, inlane: Inlane) -> None:

        self._points = 0

        inlane.observe(self, Inlane.EVENT_INLANESTART, self.ball_launch)
        inlane.observe(self, Inlane.EVENT_INLANEFAIL, self.ball_launch_fail)
        inlane.observe(self, Inlane.EVENT_INLANEPASSED, self.ball_in_game)
        inlane.observe(self, Inlane.EVENT_INLANEBACK, self.ball_returns)

    def ball_launch(self, cause, event):
        logger.info(" GAME: BALL LAUNCH (JEAH!)")

    def ball_in_game(self, cause, event):
        logger.info(" GAME: BALL IN GAME")

    def ball_launch_fail(self, cause, event):
        logger.info(" GAME: BALL LAUNCH FAILED")

    def ball_returns(self, cause, event):
        logger.info(" GAME: THE BALL IS BACK IN THE INLANE")
