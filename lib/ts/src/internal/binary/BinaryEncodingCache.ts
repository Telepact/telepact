import { BinaryEncoding } from "./BinaryEncoding";

export abstract class BinaryEncodingCache {
    abstract add(checksum: number, binaryEncodingMap: Map<string, number>): void
    abstract get(checksum: number): BinaryEncoding | undefined
    abstract remove(checksum: number): void
}