//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

export function convertMapsToObjects(value: any): any {
    if (value instanceof Map) {
        const newObj: Record<string, any> = {};
        for (const [key, val] of value.entries()) {
            newObj[key] = convertMapsToObjects(val);
        }
        return newObj;
    }

    if (Array.isArray(value)) {
        const newList = new Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            newList[index] = convertMapsToObjects(value[index]);
        }
        return newList;
    }

    if (typeof value === 'object' && value !== null) {
        const newObj: Record<string, any> = {};
        for (const key in value) {
            if (Object.prototype.hasOwnProperty.call(value, key)) {
                newObj[key] = convertMapsToObjects(value[key]);
            }
        }
        return newObj;
    }

    return value;
}
