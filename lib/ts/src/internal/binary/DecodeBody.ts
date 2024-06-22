import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { decodeKeys } from '../../internal/binary/DecodeKeys';

export function decodeBody(encodedMessageBody: Map<any, any>, binaryEncoder: BinaryEncoding): Record<string, any> {
    return decodeKeys(encodedMessageBody, binaryEncoder);
}
