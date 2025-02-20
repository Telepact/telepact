from abc import ABCMeta, abstractmethod


class BinaryEncoder(metaclass=ABCMeta):

    @abstractmethod
    def encode(self, message: list[object]) -> list[object]:
        pass

    @abstractmethod
    def decode(self, message: list[object]) -> list[object]:
        pass
