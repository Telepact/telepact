import { MsgpackUndefined } from './PackMap';
import { unpack } from './Unpack';

export function unpackMap(row: any[], header: any[]): Map<any, any> {
    const finalMap = new Map<any, any>();

    for (let j = 0; j < row.length; j += 1) {
        const key = header[j + 1];
        const value = row[j];

        if (value instanceof MsgpackUndefined) {
            continue;
        }

        if (Array.isArray(key)) {
            const nestedHeader = key as any[];
            const nestedRow = value as any[];
            const m = unpackMap(nestedRow, nestedHeader);
            const i = nestedHeader[0] as number;
            finalMap.set(i, m);
        } else {
            const unpackedValue = unpack(value);
            finalMap.set(key, unpackedValue);
        }
    }

    return finalMap;
}
