from pinball.gameengine.audio import AbstractMusic, AbstractSoundFx, AbstractSoundManager


class DummyMusic(AbstractMusic):
    def play(self):
        pass

    def stop(self):
        pass


class DummySoundFX(AbstractSoundFx):
    def play(self):
        pass


class DummySoundManager(AbstractSoundManager):
    def createMusic(self, fileName):
        return DummyMusic(fileName)

    def createSFX(self, fileName):
        return DummySoundFX(fileName)
