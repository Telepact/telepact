import { pack } from './Pack';

export function packBody(body: Record<string, any>): Record<string, any> {
    const result: Record<string, any> = {};

    for (const [key, value] of Object.entries(body)) {
        const packedValue = pack(value);
        result[key] = packedValue;
    }

    return result;
}
