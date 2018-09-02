from abc import abstractmethod


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
    def __init__(self) -> None:
        self._current_bg : AbstractMusic

    def setBg(self, music: AbstractMusic) -> None:
        if self._current_bg:
            self._current_bg.stop()
        self._current_bg = music
        music.play()

    @abstractmethod
    def createMusic(self, filename) -> AbstractMusic:
        raise NotImplementedError()

    @abstractmethod
    def createSFX(self, filename) -> AbstractSoundFx:
        raise NotImplementedError()
