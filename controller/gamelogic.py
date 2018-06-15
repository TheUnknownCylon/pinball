import logging

from pinball.gameengine.shows import ShowScript

logger = logging.getLogger(__name__)


dir = "/home/remco/pinball/soundsamples/"
dir = "/home/remco/media/"


def fadeIn(pwmled):
    i = False
    while True:
#        i = (i + 5) % 255
#        yield (lambda: pwmled.set(i), 0.05)
        i  = not i
        yield (lambda: pwmled.set(64 if i else 0), 1/60)

class MyGame():

    def __init__(self, sm, flipper_l, flipper_r, slingshot_l, slingshort_r,
                 inlane, led_1, led_2, led_3, balltrough, rgbled):

        self.leds = [led_1, led_2, led_3]
        self.active = led_1
        self._points = 0

        sound1 = sm.createSFX("{}eob_show_1.wav".format(dir))
        sound2 = sm.createSFX("{}eob_show_2.wav".format(dir))
        sound3 = sm.createSFX("{}eob_show_3.wav".format(dir))
        sound4 = sm.createSFX("{}eob_show_4.wav".format(dir))

        flash = ShowScript()
        flash.add(lambda: rgbled.set(0xFFFFFF), 0)
        flash.add(lambda: rgbled.set(0x00), 0.05)

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
        # show.start(loop=True)

        # show2 = Show(fadeIn(pwmled))
        # show2.start()

        ledShowScript = ShowScript()
        ledShowScript.add(led_1.on, 0)
        ledShowScript.add(led_1.off, 1)
        ledShowScript.add(led_2.on, 0)
        ledShowScript.add(led_2.off, 1)
        ledShowScript.add(led_3.on, 0)
        ledShowScript.add(led_3.off, 1)
        # ledShowScript.start(loop=True)

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
