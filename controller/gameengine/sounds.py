
import pygame
import io


class SoundFX():

    def __init__(self, sfile):
        sounddata = io.BytesIO(open(sfile, 'rb').read())
        self._sound = pygame.mixer.Sound(buffer=sounddata.getbuffer())

    def play(self):
        self._sound.play()


class SoundManager():

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()

    def playbg(self, sfile):
        print("Changing background song {}", sfile)
        pygame.mixer.music.load(sfile)
        pygame.mixer.music.play()

    def createSFX(self, sfile):
        return SoundFX(sfile)
