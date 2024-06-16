import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { encodeKeys } from 'uapi/internal/binary/EncodeKeys';

export function encodeBody(messageBody: Record<string, any>, binaryEncoding: BinaryEncoding): Record<any, any> {
    return encodeKeys(messageBody, binaryEncoding) as Record<any, any>;
}
