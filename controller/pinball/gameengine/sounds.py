from abc import abstractmethod

import logging

logger = logging.getLogger(__name__)

class AbstractMusic():

    def __init__(self, filename):
        pass

    @abstractmethod
    def play(self):
        raise NotImplementedError()

    @abstractmethod
    def stop(self):
        raise NotImplementedError()


class AbstractSoundFx():

    def __init__(self, filename):
        pass

    @abstractmethod
    def play(self):
        raise NotImplementedError()


class AbstractSoundManager():

    def __init__(self):
        self._current_bg = None

    def setBg(self, music):
        if self._current_bg:
            self._current_bg.stop()
        self._current_bg = music
        music.play()

    @abstractmethod
    def createMusic(self, filename):
        raise NotImplementedError()

    @abstractmethod
    def createSFX(self, filename):
        raise NotImplementedError()


###################################

import pyglet


class PygletMusic(AbstractMusic):
    def __init__(self, fileName, loop=True):
        song = pyglet.media.load(fileName)
        sourcegroup = pyglet.media.SourceGroup(song.audio_format, None)
        sourcegroup.loop = loop
        sourcegroup.queue(song)

        self._player = pyglet.media.Player()
        self._player.queue(sourcegroup)

    def play(self):
        self._player.play()

    def stop(self):
        self._player.pause()
        self._player.seek(0)


import threading


class PygletSoundManager(AbstractSoundManager):

    def createMusic(self, fileName):
        return PygletMusic(fileName)

    def createSFX(self, fileName):
        return pyglet.media.load(fileName, streaming=False)

#####################################

import pygame
import io

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
