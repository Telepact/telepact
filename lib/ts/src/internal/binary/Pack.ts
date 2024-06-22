import { packList } from 'uapi/internal/binary/PackList';

export function pack(value: any): any {
    if (Array.isArray(value)) {
        return packList(value);
    } else if (value instanceof Map) {
        const newMap: Map<any, any> = new Map();

        for (const [key, val] of value.entries()) {
            newMap.set(key, pack(val));
        }

        return newMap;
    } else {
        return value;
    }
}
