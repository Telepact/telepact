//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { BinaryEncoding, BinaryPackHeaderValue, BinaryPackSite, getBinaryPackSitePathKey } from '../../internal/binary/BinaryEncoding.js';
import { MsgpackPacked } from '../../internal/binary/PackList.js';
import { MSGPACK_UNDEFINED_VALUE } from '../../internal/binary/PackMap.js';

function isRecordLike(value: any): value is Record<string, any> | Map<any, any> {
    return value instanceof Map || (value !== null && typeof value === 'object' && !Array.isArray(value));
}

function hasRecordKey(value: Record<string, any> | Map<any, any>, key: string): boolean {
    return value instanceof Map ? value.has(key) : Object.prototype.hasOwnProperty.call(value, key);
}

function getRecordValue(value: Record<string, any> | Map<any, any>, key: string): any {
    return value instanceof Map ? value.get(key) : value[key];
}

function getRecordKeys(value: Record<string, any> | Map<any, any>): string[] {
    return value instanceof Map
        ? Array.from(value.keys()).map((key) => String(key))
        : Object.keys(value);
}

function getRecordEntries(value: Record<string, any> | Map<any, any>): Array<[string, any]> {
    return value instanceof Map
        ? Array.from(value.entries()).map(([key, item]) => [String(key), item] as [string, any])
        : Object.entries(value);
}

function encodePlainValue(value: any, binaryEncoding: BinaryEncoding): any {
    const encodeMap = binaryEncoding.encodeMap;
    const stack: Array<{ type: 'list'; iterator: IterableIterator<[number, any]>; target: any[] } | { type: 'map'; iterator: IterableIterator<[string, any]>; target: Map<any, any> }> = [];
    let finalRoot: any;

    if (Array.isArray(value)) {
        finalRoot = new Array(value.length);
        stack.push({ type: 'list', iterator: value.entries(), target: finalRoot });
    } else if (isRecordLike(value)) {
        finalRoot = new Map<any, any>();
        stack.push({ type: 'map', iterator: getRecordEntries(value)[Symbol.iterator](), target: finalRoot });
    } else {
        return value;
    }

    while (stack.length > 0) {
        const frame = stack[stack.length - 1]!;
        const step = frame.iterator.next();
        if (step.done) {
            stack.pop();
            continue;
        }

        if (frame.type === 'map') {
            const [key, item] = step.value;
            const encodedKey = encodeMap.get(key) ?? key;
            if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target.set(encodedKey, childTarget);
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget });
            } else if (isRecordLike(item)) {
                const childTarget = new Map<any, any>();
                frame.target.set(encodedKey, childTarget);
                stack.push({ type: 'map', iterator: getRecordEntries(item)[Symbol.iterator](), target: childTarget });
            } else {
                frame.target.set(encodedKey, item);
            }
        } else {
            const [index, item] = step.value;
            if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target[index] = childTarget;
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget });
            } else if (isRecordLike(item)) {
                const childTarget = new Map<any, any>();
                frame.target[index] = childTarget;
                stack.push({ type: 'map', iterator: getRecordEntries(item)[Symbol.iterator](), target: childTarget });
            } else {
                frame.target[index] = item;
            }
        }
    }

    return finalRoot;
}

function encodePackedRow(item: Record<string, any> | Map<any, any>, header: BinaryPackHeaderValue[], binaryEncoding: BinaryEncoding): any[] {
    const rowRoot = new Array(header.length - 1).fill(MSGPACK_UNDEFINED_VALUE);
    const stack: Array<{ source: Record<string, any> | Map<any, any>; header: BinaryPackHeaderValue[]; row: any[]; index: number }> = [
        { source: item, header, row: rowRoot, index: 1 },
    ];

    while (stack.length > 0) {
        const frame = stack.pop()!;
        let currentSource = frame.source;
        let currentHeader = frame.header;
        let currentRow = frame.row;
        let index = frame.index;

        const getAllowedKeys = (header: BinaryPackHeaderValue[]): Set<string> => {
            const nextAllowedKeys = new Set<string>();
            for (let headerIndex = 1; headerIndex < header.length; headerIndex += 1) {
                const allowedHeaderItem = header[headerIndex]!;
                nextAllowedKeys.add(String(Array.isArray(allowedHeaderItem) ? allowedHeaderItem[0] : allowedHeaderItem));
            }
            return nextAllowedKeys;
        };
        let allowedKeys = getAllowedKeys(currentHeader);

        while (index < currentHeader.length) {
            for (const sourceKey of getRecordKeys(currentSource)) {
                if (!allowedKeys.has(sourceKey)) {
                    throw new TypeError('Packed row contains unknown field');
                }
            }

            const headerItem = currentHeader[index]!;
            const rowIndex = index - 1;
            if (Array.isArray(headerItem)) {
                const fieldKey = String(headerItem[0]);
                if (!hasRecordKey(currentSource, fieldKey)) {
                    index += 1;
                    continue;
                }
                const value = getRecordValue(currentSource, fieldKey);
                if (!isRecordLike(value)) {
                    throw new TypeError('Packed nested struct value must be a map');
                }
                const nestedRow = new Array(headerItem.length - 1).fill(MSGPACK_UNDEFINED_VALUE);
                currentRow[rowIndex] = nestedRow;
                stack.push({ source: currentSource, header: currentHeader, row: currentRow, index: index + 1 });
                currentSource = value;
                currentHeader = headerItem;
                currentRow = nestedRow;
                allowedKeys = getAllowedKeys(currentHeader);
                index = 1;
                continue;
            }

            const fieldKey = String(headerItem);
            if (hasRecordKey(currentSource, fieldKey)) {
                const value = getRecordValue(currentSource, fieldKey);
                if (Array.isArray(value) || value instanceof Map || (value !== null && typeof value === 'object')) {
                    currentRow[rowIndex] = encodePlainValue(value, binaryEncoding);
                } else {
                    currentRow[rowIndex] = value;
                }
            }
            index += 1;
        }
    }

    return rowRoot;
}

function encodePackedList(values: any[], packSite: BinaryPackSite, binaryEncoding: BinaryEncoding): any[] {
    const packedList: any[] = [new MsgpackPacked(), packSite.encodedHeader];
    try {
        for (const item of values) {
            if (!isRecordLike(item)) {
                throw new TypeError('Packed list items must be maps');
            }
            packedList.push(encodePackedRow(item, packSite.header, binaryEncoding));
        }
        return packedList;
    } catch {
        return encodePlainValue(values, binaryEncoding);
    }
}

export function encodeBody(messageBody: Record<string, any>, binaryEncoder: BinaryEncoding, packed: boolean = false): Map<any, any> {
    const encodeMap = binaryEncoder.encodeMap;
    const packSitesByPath = packed ? binaryEncoder.packSitesByPath : new Map<string, BinaryPackSite>();
    const finalRoot = new Map<any, any>();
    const stack: Array<{ type: 'map'; iterator: IterableIterator<[string, any]>; target: Map<any, any>; path: string[]; trackPaths: boolean } | { type: 'list'; iterator: IterableIterator<[number, any]>; target: any[]; path: string[]; trackPaths: boolean }> = [
        { type: 'map', iterator: Object.entries(messageBody)[Symbol.iterator](), target: finalRoot, path: [], trackPaths: true },
    ];

    while (stack.length > 0) {
        const frame = stack[stack.length - 1]!;
        const step = frame.iterator.next();
        if (step.done) {
            stack.pop();
            continue;
        }

        if (frame.type === 'map') {
            const [key, item] = step.value;
            const encodedKey = encodeMap.get(key) ?? key;
            const nextPath = frame.trackPaths ? [...frame.path, key] : [];
            if (Array.isArray(item)) {
                const packSite = frame.trackPaths ? packSitesByPath.get(getBinaryPackSitePathKey(nextPath)) : undefined;
                if (packSite !== undefined) {
                    frame.target.set(encodedKey, encodePackedList(item, packSite, binaryEncoder));
                } else {
                    const childTarget = new Array(item.length);
                    frame.target.set(encodedKey, childTarget);
                    stack.push({ type: 'list', iterator: item.entries(), target: childTarget, path: [], trackPaths: false });
                }
            } else if (item !== null && typeof item === 'object') {
                const childTarget = new Map<any, any>();
                frame.target.set(encodedKey, childTarget);
                const childEntries = item instanceof Map
                    ? Array.from(item.entries()).map(([childKey, childValue]) => [String(childKey), childValue] as [string, any])
                    : Object.entries(item);
                stack.push({ type: 'map', iterator: childEntries[Symbol.iterator](), target: childTarget, path: nextPath, trackPaths: frame.trackPaths });
            } else {
                frame.target.set(encodedKey, item);
            }
        } else {
            const [index, item] = step.value;
            if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target[index] = childTarget;
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget, path: [], trackPaths: false });
            } else if (item !== null && typeof item === 'object') {
                const childTarget = new Map<any, any>();
                frame.target[index] = childTarget;
                const childEntries = item instanceof Map
                    ? Array.from(item.entries()).map(([childKey, childValue]) => [String(childKey), childValue] as [string, any])
                    : Object.entries(item);
                stack.push({ type: 'map', iterator: childEntries[Symbol.iterator](), target: childTarget, path: [], trackPaths: false });
            } else {
                frame.target[index] = item;
            }
        }
    }

    return finalRoot;
}
