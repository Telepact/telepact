import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';
import { encodeKeys } from 'uapi/internal/binary/EncodeKeys';

export function encodeBody(messageBody: Record<string, any>, binaryEncoder: BinaryEncoding): Map<any, any> {
    return encodeKeys(messageBody, binaryEncoder);
}
