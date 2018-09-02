import pyglet

from pinball.gameengine.audio import AbstractMusic, AbstractSoundManager


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


class PygletSoundManager(AbstractSoundManager):
    def createMusic(self, fileName):
        return PygletMusic(fileName)

    def createSFX(self, fileName):
        return pyglet.media.load(fileName, streaming=False)
