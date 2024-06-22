import { ClientBinaryStrategy } from 'uapi/ClientBinaryStrategy';
import { clientBinaryEncode } from 'uapi/internal/binary/ClientBinaryEncode';
import { clientBinaryDecode } from 'uapi/internal/binary/ClientBinaryDecode';
import { BinaryEncoder } from './BinaryEncoder';
import { BinaryEncoding } from './BinaryEncoding';

export class ClientBinaryEncoder implements BinaryEncoder {
    private readonly recentBinaryEncoders: Map<number, BinaryEncoding>;
    private readonly binaryChecksumStrategy: ClientBinaryStrategy;

    constructor(binaryChecksumStrategy: ClientBinaryStrategy) {
        this.recentBinaryEncoders = new Map<number, BinaryEncoding>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    encode(message: any[]): any[] {
        return clientBinaryEncode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

    decode(message: any[]): any[] {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }
}
