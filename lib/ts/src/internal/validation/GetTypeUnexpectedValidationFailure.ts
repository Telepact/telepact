//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { getType } from '../../internal/types/GetType.js';

export function getTypeUnexpectedValidationFailure(path: any[], value: any, expectedType: string): ValidationFailure[] {
    const actualType = getType(value);
    const data: { [key: string]: any } = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new ValidationFailure(path, 'TypeUnexpected', data)];
}
