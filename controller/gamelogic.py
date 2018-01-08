import logging

from pinball.gameengine.shows import ShowScript
from pinball.gamedevices.timer import GameTimer

logger = logging.getLogger(__name__)


class MyGame():

    def __init__(self, sm, flipper_l, flipper_r, slingshot_l, slingshort_r,
                 inlane, led_1, led_2, led_3, rgbled):

        self.leds = [led_1, led_2, led_3]
        self.active = led_1
        self._points = 0

        sound1 = sm.createSFX("""/home/remco/pinball/soundsamples/eob_show_1.wav""")
        sound2 = sm.createSFX("""/home/remco/pinball/soundsamples/eob_show_2.wav""")
        sound3 = sm.createSFX("""/home/remco/pinball/soundsamples/eob_show_3.wav""")
        sound4 = sm.createSFX("""/home/remco/pinball/soundsamples/eob_show_4.wav""")
        music1 = sm.createMusic("""/home/remco/pinball/soundsamples/main_new.wav""")

        flash = ShowScript()
        flash.add(lambda: rgbled.set(0xFFFFFF), 0)
        flash.add(lambda: rgbled.set(0x00), 0.1)

        show = ShowScript()
        show.add(sound1.play, 0)
        show.add(flash.start, 0)
        show.add(sound2.play, 1)
        show.add(flash.start, 0)
        show.add(sound3.play, 1)
        show.add(flash.start, 0)
        show.add(sound4.play, 1.5)
        show.add(flash.start, 0)
        show.add(sound4.play, 0.5)
        show.add(flash.start, 0)
        show.add(sound4.play, 0.5)
        show.add(flash.start, 0)
        show.add(lambda: (), 1.5)
        # show.add(lambda: sm.setBg(music1), 1.5)
        show.start(loop=True)

        ledShowScript = ShowScript()
        ledShowScript.add(led_1.on, 0)
        ledShowScript.add(led_1.off, 1)
        ledShowScript.add(led_2.on, 0)
        ledShowScript.add(led_2.off, 1)
        ledShowScript.add(led_3.on, 0)
        ledShowScript.add(led_3.off, 1)
        ledShowScript.start(loop=True)

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
