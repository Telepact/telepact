class BinaryEncoding:
    def __init__(self, binary_encoding_map: dict[str, int], checksum: int) -> None:
        self.encode_map: dict[str, int] = binary_encoding_map
        self.decode_map: dict[int, str] = {
            v: k for k, v in binary_encoding_map.items()}
        self.checksum: int = checksum
