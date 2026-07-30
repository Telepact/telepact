//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { getType } from '../../internal/types/GetType.js';

export function getTypeUnexpectedParseFailure(
    documentName: string,
    path: any[],
    value: any,
    expectedType: string,
): SchemaParseFailure[] {
    const actualType = getType(value);
    const data: { actual: { [key: string]: any }; expected: { [key: string]: any } } = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new SchemaParseFailure(documentName, path, 'TypeUnexpected', data)];
}
