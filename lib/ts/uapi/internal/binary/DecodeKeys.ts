import { BinaryEncoding } from 'uapi.internal.binary.BinaryEncoding';
import { BinaryEncodingMissing } from 'uapi.internal.binary.BinaryEncodingMissing';

export function decodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (typeof given === 'object' && given !== null) {
        const newDict: { [key: string]: any } = {};

        for (const [key, value] of Object.entries(given)) {
            let newKey: string;

            if (typeof key === 'string') {
                newKey = key;
            } else {
                const possibleNewKey = binaryEncoder.decodeMap.get(key);

                if (possibleNewKey === undefined) {
                    throw new BinaryEncodingMissing(key);
                }

                newKey = possibleNewKey;
            }

            const encodedValue = decodeKeys(value, binaryEncoder);
            newDict[newKey] = encodedValue;
        }

        return newDict;
    } else if (Array.isArray(given)) {
        return given.map((item) => decodeKeys(item, binaryEncoder));
    } else {
        return given;
    }
}
