import pygame
import io

from pinball.gameengine.audio import AbstractMusic, AbstractSoundManager


class PyGameMusic():
    def __init__(self, fileName):
        self._fileName = fileName

    def play(self):
        pygame.mixer.music.load(self._fileName)
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()


class PyGameSoundFX():
    def __init__(self, fileName):
        sounddata = io.BytesIO(open(fileName, 'rb').read())
        self._sound = pygame.mixer.Sound(buffer=sounddata.getbuffer())

    def play(self):
        self._sound.play()


class PyGameSoundManager(AbstractSoundManager):
    def __init__(self):
        AbstractSoundManager.__init__(self)
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()

    def createMusic(self, fileName):
        return PyGameMusic(fileName)

    def createSFX(self, fileName):
        return PyGameSoundFX(fileName)
