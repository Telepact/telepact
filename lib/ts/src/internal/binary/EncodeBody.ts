import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { encodeKeys } from '../../internal/binary/EncodeKeys';

export function encodeBody(messageBody: Record<string, any>, binaryEncoder: BinaryEncoding): Map<any, any> {
    return encodeKeys(messageBody, binaryEncoder);
}
