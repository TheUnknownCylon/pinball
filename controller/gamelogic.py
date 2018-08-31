import logging

from pinball.gameengine.shows import ShowScript

logger = logging.getLogger(__name__)


dir = "/home/remco/pinball/soundsamples/"
dir = "/home/remco/media/"

class MyGame():

    def __init__(self, sm, flipper_l, flipper_r, slingshot_l, slingshort_r,
                 inlane):

        self._points = 0

        inlane.registerForInlaneStart(self, self.ball_launch)
        inlane.registerForInlaneFail(self, self.ball_launch_fail)
        inlane.registerForInlanePassed(self, self.ball_in_game)
        inlane.registerForInlaneBack(self, self.ball_returns)

    def ball_launch(self):
        logger.info(" GAME: BALL LAUNCH (JEAH!)")

    def ball_in_game(self):
        logger.info(" GAME: BALL IN GAME")

    def ball_launch_fail(self):
        logger.info(" GAME: BALL LAUNCH FAILED")

    def ball_returns(self):
        logger.info(" GAME: THE BALL IS BACK IN THE INLANE")
