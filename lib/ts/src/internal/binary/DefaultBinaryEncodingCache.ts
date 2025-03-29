import { BinaryEncodingCache } from "../../internal/binary/BinaryEncodingCache";
import { BinaryEncoding } from "./BinaryEncoding";

export class DefaultBinaryEncodingCache extends BinaryEncodingCache {
    private recentBinaryEncoders: Map<number, BinaryEncoding>;

    constructor() {
        super();
        this.recentBinaryEncoders = new Map<number, BinaryEncoding>();
    }

    add(checksum: number, binaryEncodingMap: Map<string, number>): void {
        const binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum);
        this.recentBinaryEncoders.set(checksum, binaryEncoding);
    }

    get(checksum: number): BinaryEncoding | undefined {
        return this.recentBinaryEncoders.get(checksum);
    }

    remove(checksum: number): void {
        this.recentBinaryEncoders.delete(checksum);
    }
}
