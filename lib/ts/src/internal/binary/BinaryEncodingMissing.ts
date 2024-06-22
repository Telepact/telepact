export class BinaryEncodingMissing extends Error {
    constructor(key: object) {
        super(`Missing binary encoding for ${String(key)}`);
    }
}
