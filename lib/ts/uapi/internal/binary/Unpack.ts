import { unpackList } from './UnpackList';

export function unpack(value: any): any {
    if (Array.isArray(value)) {
        return unpackList(value);
    } else if (value instanceof Map) {
        const newMap: Map<any, any> = new Map();

        for (const [key, val] of value.entries()) {
            newMap.set(key, unpack(val));
        }

        return newMap;
    } else {
        return value;
    }
}
