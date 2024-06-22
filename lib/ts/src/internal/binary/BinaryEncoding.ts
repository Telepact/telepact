export class BinaryEncoding {
    public readonly encodeMap: Map<string, number>;
    public readonly decodeMap: Map<number, string>;
    public readonly checksum: number;

    constructor(binaryEncodingMap: Map<string, number>, checksum: number) {
        this.encodeMap = binaryEncodingMap;
        const decodeList: [number, string][] = [...binaryEncodingMap.entries()].map((e: [string, number]) => [
            e[1],
            e[0],
        ]);
        this.decodeMap = new Map(decodeList);
        this.checksum = checksum;
    }
}
