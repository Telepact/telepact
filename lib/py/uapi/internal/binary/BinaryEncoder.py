from abc import ABC, abstractmethod


class BinaryEncoder(ABC):

    @abstractmethod
    def encode(self, message: list[object]) -> list[object]:
        pass

    @abstractmethod
    def decode(self, message: list[object]) -> list[object]:
        pass
