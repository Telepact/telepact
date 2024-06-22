import crc32 from 'crc-32';

export function createChecksum(value: string): number {
    const checksum = crc32.str(value);
    return checksum >>> 0;
}
