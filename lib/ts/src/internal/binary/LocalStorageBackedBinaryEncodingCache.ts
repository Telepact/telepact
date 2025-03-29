import { BinaryEncodingCache } from "../../internal/binary/BinaryEncodingCache";
import { BinaryEncoding } from "./BinaryEncoding";

export class LocalStorageBackedBinaryEncodingCache extends BinaryEncodingCache {
    private recentBinaryEncoders: Map<number, BinaryEncoding>;
    private namespace: string;

    constructor(namespace: string) {
        super();

        this.namespace = namespace;

        // Load initial state of recentBinaryEncoders from local storage
        const storedData = localStorage.getItem(this.namespace + '-telepact-encoding');
        if (storedData) {
            const parsedData = JSON.parse(storedData);
            this.recentBinaryEncoders = this.mapFromJSON(parsedData);
        } else {
            this.recentBinaryEncoders = new Map<number, BinaryEncoding>();
        }
    }

    add(checksum: number, binaryEncodingMap: Map<string, number>): void {
        const binaryEncoding = new BinaryEncoding(binaryEncodingMap, checksum);
        this.recentBinaryEncoders.set(checksum, binaryEncoding);

        this.saveToLocalStorage();
    }

    get(checksum: number): BinaryEncoding | undefined {
        return this.recentBinaryEncoders.get(checksum);
    }

    remove(checksum: number): void {
        this.recentBinaryEncoders.delete(checksum);

        // Rewrite recentBinaryEncoders to local storage
        this.saveToLocalStorage();
    }

    private saveToLocalStorage(): void {
        const serializedData = this.mapToJSON(this.recentBinaryEncoders);
        localStorage.setItem(this.namespace + '-telepact-encoding', JSON.stringify(serializedData));
    }

    private mapToJSON(map: Map<number, BinaryEncoding>): Record<string, any> {
        return Object.fromEntries(
            Array.from(map.entries()).map(([key, value]) => [
                key,
                { binaryEncodingMap: Array.from(value.encodeMap.entries()), checksum: value.checksum },
            ])
        );
    }

    private mapFromJSON(json: Record<string, any>): Map<number, BinaryEncoding> {
        return new Map<number, BinaryEncoding>(
            Object.entries(json).map(([key, value]) => [
                Number(key),
                new BinaryEncoding(new Map(value.binaryEncodingMap), value.checksum),
            ])
        );
    }
}
