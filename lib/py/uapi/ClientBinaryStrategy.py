from typing import list


class ClientBinaryStrategy:
    """
    The strategy used by the client to maintain binary encodings compatible with
    the server.
    """

    def update(self, checksum: int) -> None:
        """
        Update the strategy according to a recent binary encoding checksum returned
        by the server.

        Args:
            checksum: The checksum returned by the server.
        """
        pass

    def get_current_checksums(self) -> list[int]:
        """
        Get the current binary encoding strategy as a list of binary encoding
        checksums that should be sent to the server.

        Returns:
            A list of checksums.
        """
        pass
