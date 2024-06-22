import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';
import { BinaryEncodingMissing } from '../../internal/binary/BinaryEncodingMissing';

export function decodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (given instanceof Map) {
        const newMap: { [key: string]: any } = {};

        for (const [key, value] of given.entries()) {
            const finalKey = typeof key === 'string' ? key : binaryEncoder.decodeMap.get(key);

            if (finalKey === undefined) {
                throw new BinaryEncodingMissing(key);
            }

            const decodedValue = decodeKeys(value, binaryEncoder);
            newMap[finalKey] = decodedValue;
        }

        return newMap;
    } else if (Array.isArray(given)) {
        return given.map((value) => decodeKeys(value, binaryEncoder));
    } else {
        return given;
    }
}
