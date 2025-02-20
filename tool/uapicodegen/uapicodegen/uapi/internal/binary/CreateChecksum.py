import zlib


def create_checksum(value: str) -> int:
    checksum = zlib.crc32(value.encode('utf-8'))
    # Convert to 32-bit two's complement
    if checksum & 0x80000000:
        checksum = checksum - 0x100000000
    return checksum
