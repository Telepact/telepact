import { unpack } from './Unpack';

export function unpackBody(body: Map<any, any>): Map<any, any> {
    const result: Map<any, any> = new Map();

    for (const [key, value] of body.entries()) {
        const unpackedValue = unpack(value);
        result.set(key, unpackedValue);
    }

    return result;
}
