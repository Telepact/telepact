import { unpackList } from './UnpackList';

export function unpack(value: any): any {
    if (Array.isArray(value)) {
        return unpackList(value);
    } else if (typeof value === 'object' && value !== null) {
        const newObject: any = {};
        for (const key in value) {
            if (value.hasOwnProperty(key)) {
                newObject[key] = unpack(value[key]);
            }
        }
        return newObject;
    } else {
        return value;
    }
}
