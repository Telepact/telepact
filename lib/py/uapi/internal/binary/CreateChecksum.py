import zlib


def create_checksum(value: str) -> int:
    checksum = zlib.crc32(value.encode('utf-8'))
    return checksum
