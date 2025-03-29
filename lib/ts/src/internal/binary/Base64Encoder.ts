export abstract class Base64Encoder {
    abstract encode(message: object[]): object[];
    abstract decode(message: object[]): object[];
}