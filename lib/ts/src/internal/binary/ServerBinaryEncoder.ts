import { BinaryEncoder } from './BinaryEncoder';
import { BinaryEncoding } from './BinaryEncoding';
import { serverBinaryEncode } from './ServerBinaryEncode';
import { serverBinaryDecode } from './ServerBinaryDecode';

export class ServerBinaryEncoder implements BinaryEncoder {
    private binaryEncoder: BinaryEncoding;

    constructor(binaryEncoder: BinaryEncoding) {
        this.binaryEncoder = binaryEncoder;
    }

    encode(message: any[]): any[] {
        return serverBinaryEncode(message, this.binaryEncoder);
    }

    decode(message: any[]): any[] {
        return serverBinaryDecode(message, this.binaryEncoder);
    }
}
