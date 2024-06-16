import { ClientBinaryStrategy } from 'uapi/ClientBinaryStrategy';
import { clientBinaryEncode } from 'uapi/internal/binary/ClientBinaryEncode';
import { clientBinaryDecode } from 'uapi/internal/binary/ClientBinaryDecode';

export class ClientBinaryEncoder {
    private recentBinaryEncoders: { [key: number]: any } = {};
    private binaryChecksumStrategy: ClientBinaryStrategy;

    constructor(binaryChecksumStrategy: ClientBinaryStrategy) {
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    encode(message: any[]): any[] {
        return clientBinaryEncode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

    decode(message: any[]): any[] {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }
}
