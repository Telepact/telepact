import { packList } from './uapi/internal/binary/PackList';

export function pack(value: any): any {
    if (Array.isArray(value)) {
        return packList(value);
    } else if (typeof value === 'object' && value !== null) {
        const newMap: any = {};

        for (const key in value) {
            if (value.hasOwnProperty(key)) {
                newMap[key] = pack(value[key]);
            }
        }

        return newMap;
    } else {
        return value;
    }
}
