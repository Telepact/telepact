import { ExtType } from 'msgpack';
import { UNDEFINED_BYTE } from './PackMap';
import { unpack } from './Unpack';

export function unpackMap(row: any[], header: any[]): { [key: number]: any } {
    const finalMap: { [key: number]: any } = {};

    for (let j = 0; j < row.length; j++) {
        const key = header[j + 1];
        const value = row[j];

        if (value instanceof ExtType && value.code === UNDEFINED_BYTE) {
            continue;
        }

        if (Array.isArray(key)) {
            const nestedHeader = key;
            const nestedRow = value as any[];
            const m = unpackMap(nestedRow, nestedHeader);
            const i = nestedHeader[0];

            finalMap[i] = m;
        } else {
            const i = key;
            const unpackedValue = unpack(value);

            finalMap[i] = unpackedValue;
        }
    }

    return finalMap;
}
