from abc import ABCMeta, abstractmethod


class ClientBinaryStrategy(metaclass=ABCMeta):
    """
    The strategy used by the client to maintain binary encodings compatible with
    the server.
    """

    @abstractmethod
    def update(self, checksum: int) -> None:
        """
        Update the strategy according to a recent binary encoding checksum returned
        by the server.

        Args:
            checksum: The checksum returned by the server.
        """
        pass

    @abstractmethod
    def get_current_checksums(self) -> list[int]:
        """
        Get the current binary encoding strategy as a list of binary encoding
        checksums that should be sent to the server.

        Returns:
            A list of checksums.
        """
        pass
