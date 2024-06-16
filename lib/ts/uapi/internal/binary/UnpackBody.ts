import { unpack } from './Unpack';

export function unpackBody(body: Record<string, any>): Record<string, any> {
    const result: Record<string, any> = {};

    for (const [key, value] of Object.entries(body)) {
        const unpackedValue = unpack(value);
        result[key] = unpackedValue;
    }

    return result;
}
