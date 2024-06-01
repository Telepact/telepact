import zlib


def create_checksum(value: str):
    checksum = zlib.crc32(value.encode('utf-8'))
    return checksum
