import { BinaryEncoding } from 'uapi/internal/binary/BinaryEncoding';

export function encodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (given === null || given === undefined) {
        return given;
    } else if (typeof given === 'object' && !Array.isArray(given)) {
        const newMap = new Map<any, any>();

        for (const [key, value] of Object.entries(given)) {
            const finalKey = binaryEncoder.encodeMap.has(key) ? binaryEncoder.encodeMap.get(key) : key;
            const encodedValue = encodeKeys(value, binaryEncoder);

            newMap.set(finalKey, encodedValue);
        }

        return newMap;
    } else if (Array.isArray(given)) {
        return given.map((value) => encodeKeys(value, binaryEncoder));
    } else {
        return given;
    }
}
