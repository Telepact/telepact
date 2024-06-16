export abstract class BinaryEncoder {
    abstract encode(message: object[]): object[];
    abstract decode(message: object[]): object[];
}
