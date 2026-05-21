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
import { BinaryEncodingMissing } from '../../internal/binary/BinaryEncodingMissing.js';
import { MsgpackPacked } from '../../internal/binary/PackList.js';
import { MsgpackUndefined } from '../../internal/binary/PackMap.js';

function decodeKey(key: any, binaryEncoding: BinaryEncoding): string {
    if (typeof key === 'string') {
        return key;
    }
    const decodedKey = binaryEncoding.decodeTable[key as number];
    if (decodedKey === undefined) {
        throw new BinaryEncodingMissing(key as object);
    }
    return decodedKey;
}

function decodePlainValue(value: any, binaryEncoding: BinaryEncoding): any {
    const stack: Array<{ type: 'list'; iterator: IterableIterator<[number, any]>; target: any[] } | { type: 'map'; iterator: IterableIterator<[any, any]>; target: Record<string, any> }> = [];
    let finalRoot: any;

    if (Array.isArray(value)) {
        finalRoot = new Array(value.length);
        stack.push({ type: 'list', iterator: value.entries(), target: finalRoot });
    } else if (value instanceof Map) {
        finalRoot = {};
        stack.push({ type: 'map', iterator: value.entries(), target: finalRoot });
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
            const [rawKey, item] = step.value;
            const decodedKey = decodeKey(rawKey, binaryEncoding);
            if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target[decodedKey] = childTarget;
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget });
            } else if (item instanceof Map) {
                const childTarget: Record<string, any> = {};
                frame.target[decodedKey] = childTarget;
                stack.push({ type: 'map', iterator: item.entries(), target: childTarget });
            } else {
                frame.target[decodedKey] = item;
            }
        } else {
            const [index, item] = step.value;
            if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target[index] = childTarget;
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget });
            } else if (item instanceof Map) {
                const childTarget: Record<string, any> = {};
                frame.target[index] = childTarget;
                stack.push({ type: 'map', iterator: item.entries(), target: childTarget });
            } else {
                frame.target[index] = item;
            }
        }
    }

    return finalRoot;
}

function decodePackedRow(row: any[], header: BinaryPackHeaderValue[], binaryEncoding: BinaryEncoding): Record<string, any> {
    const finalRoot: Record<string, any> = {};
    const stack: Array<{ row: any[]; header: BinaryPackHeaderValue[]; target: Record<string, any>; index: number }> = [
        { row, header, target: finalRoot, index: 1 },
    ];

    while (stack.length > 0) {
        const frame = stack.pop()!;
        let currentRow = frame.row;
        let currentHeader = frame.header;
        let currentTarget = frame.target;
        let index = frame.index;

        while (index < currentHeader.length) {
            const headerItem = currentHeader[index]!;
            const rowIndex = index - 1;
            if (rowIndex >= currentRow.length) {
                break;
            }
            const value = currentRow[rowIndex];
            if (value instanceof MsgpackUndefined) {
                index += 1;
                continue;
            }

            if (Array.isArray(headerItem)) {
                const fieldKey = String(headerItem[0]);
                if (!Array.isArray(value)) {
                    throw new TypeError('Packed nested row value must be a list');
                }
                const nestedTarget: Record<string, any> = {};
                currentTarget[fieldKey] = nestedTarget;
                stack.push({ row: currentRow, header: currentHeader, target: currentTarget, index: index + 1 });
                currentRow = value;
                currentHeader = headerItem;
                currentTarget = nestedTarget;
                index = 1;
                continue;
            }

            if (Array.isArray(value) || value instanceof Map) {
                currentTarget[String(headerItem)] = decodePlainValue(value, binaryEncoding);
            } else {
                currentTarget[String(headerItem)] = value;
            }
            index += 1;
        }
    }

    return finalRoot;
}

function decodePackedList(value: any[], packSite: BinaryPackSite, binaryEncoding: BinaryEncoding): any[] {
    if (value.length === 0) {
        return [];
    }
    if (!(value[0] instanceof MsgpackPacked)) {
        return decodePlainValue(value, binaryEncoding);
    }
    if (value.length < 2) {
        return [];
    }

    const finalList: any[] = [];
    try {
        for (const row of value.slice(2)) {
            if (!Array.isArray(row)) {
                throw new TypeError('Packed row must be a list');
            }
            finalList.push(decodePackedRow(row, packSite.header, binaryEncoding));
        }
        return finalList;
    } catch {
        return decodePlainValue(value, binaryEncoding);
    }
}

export function decodeBody(encodedMessageBody: Map<any, any>, binaryEncoder: BinaryEncoding, packed: boolean = false): Record<string, any> {
    const packSitesByEncodedPath = packed ? binaryEncoder.packSitesByEncodedPath : new Map<string, BinaryPackSite>();
    const finalRoot: Record<string, any> = {};
    const stack: Array<{ type: 'map'; iterator: IterableIterator<[any, any]>; target: Record<string, any>; path: number[]; trackPaths: boolean } | { type: 'list'; iterator: IterableIterator<[number, any]>; target: any[]; path: number[]; trackPaths: boolean }> = [
        { type: 'map', iterator: encodedMessageBody.entries(), target: finalRoot, path: [], trackPaths: true },
    ];

    while (stack.length > 0) {
        const frame = stack[stack.length - 1]!;
        const step = frame.iterator.next();
        if (step.done) {
            stack.pop();
            continue;
        }

        if (frame.type === 'map') {
            const [rawKey, item] = step.value;
            const decodedKey = decodeKey(rawKey, binaryEncoder);
            const nextPath = frame.trackPaths && typeof rawKey === 'number' ? [...frame.path, rawKey] : [];
            const packSite = frame.trackPaths && Array.isArray(item)
                ? packSitesByEncodedPath.get(getBinaryPackSitePathKey(nextPath))
                : undefined;
            if (packSite !== undefined) {
                frame.target[decodedKey] = decodePackedList(item, packSite, binaryEncoder);
            } else if (item instanceof Map) {
                const childTarget: Record<string, any> = {};
                frame.target[decodedKey] = childTarget;
                stack.push({ type: 'map', iterator: item.entries(), target: childTarget, path: nextPath, trackPaths: frame.trackPaths });
            } else if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target[decodedKey] = childTarget;
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget, path: [], trackPaths: false });
            } else {
                frame.target[decodedKey] = item;
            }
        } else {
            const [index, item] = step.value;
            if (item instanceof Map) {
                const childTarget: Record<string, any> = {};
                frame.target[index] = childTarget;
                stack.push({ type: 'map', iterator: item.entries(), target: childTarget, path: [], trackPaths: false });
            } else if (Array.isArray(item)) {
                const childTarget = new Array(item.length);
                frame.target[index] = childTarget;
                stack.push({ type: 'list', iterator: item.entries(), target: childTarget, path: [], trackPaths: false });
            } else {
                frame.target[index] = item;
            }
        }
    }

    return finalRoot;
}
