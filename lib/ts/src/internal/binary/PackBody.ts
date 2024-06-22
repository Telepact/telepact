import { pack } from './Pack';

export function packBody(body: Map<any, any>): Map<any, any> {
    const result: Map<any, any> = new Map();

    for (const [key, value] of body.entries()) {
        const packedValue = pack(value);
        result.set(key, packedValue);
    }

    return result;
}
