import logging

from pinball.gamedevices.timer import GameTimer

logger = logging.getLogger(__name__)


class MyGame():

    def __init__(self, flipper_l, flipper_r, slingshot_l, slingshort_r,
                 inlane, led_1, led_2, led_3):

        self.leds = [led_1, led_2, led_3]
        self.active = led_1
        self.ledon = 0
        self.ledtimer = GameTimer(1)
        self.ledtimer.observe(self, self.nextLight)
        self.ledtimer.start()

        self._points = 0

        inlane.registerForInlaneStart(self, self.ball_launch)
        inlane.registerForInlaneFail(self, self.ball_launch_fail)
        inlane.registerForInlanePassed(self, self.ball_in_game)
        inlane.registerForInlaneBack(self, self.ball_returns)

    def nextLight(self, x, y):
        self.ledtimer.restart()
        self.ledon = (self.ledon + 1) % 3
        self.active.off()
        self.active = self.leds[self.ledon]
        self.active.on()

    def ball_launch(self):
        logger.info(" GAME: BALL LAUNCH (JEAH!)")

    def ball_in_game(self):
        logger.info(" GAME: BALL IN GAME")

    def ball_launch_fail(self):
        logger.info(" GAME: BALL LAUNCH FAILED")

    def ball_returns(self):
        logger.info(" GAME: THE BALL IS BACK IN THE INLANE")
