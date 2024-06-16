export class BinaryEncoding {
    encodeMap: Record<string, number>;
    decodeMap: Record<number, string>;
    checksum: number;

    constructor(binaryEncodingMap: Record<string, number>, checksum: number) {
        this.encodeMap = binaryEncodingMap;
        this.decodeMap = {};
        for (const [key, value] of Object.entries(binaryEncodingMap)) {
            this.decodeMap[value] = key;
        }
        this.checksum = checksum;
    }
}
