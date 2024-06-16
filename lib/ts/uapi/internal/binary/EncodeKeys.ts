import { BinaryEncoding } from 'uapi.internal.binary.BinaryEncoding';

export function encodeKeys(given: any, binaryEncoding: BinaryEncoding): any {
    if (given === null || given === undefined) {
        return given;
    } else if (typeof given === 'object') {
        const newObject: { [key: string]: any } = {};

        for (const key in given) {
            if (given.hasOwnProperty(key)) {
                const finalKey = binaryEncoding.encodeMap[key] || key;
                const encodedValue = encodeKeys(given[key], binaryEncoding);

                newObject[finalKey] = encodedValue;
            }
        }

        return newObject;
    } else if (Array.isArray(given)) {
        return given.map((item) => encodeKeys(item, binaryEncoding));
    } else {
        return given;
    }
}
