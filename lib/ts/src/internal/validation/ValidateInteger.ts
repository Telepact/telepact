//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { integerName } from '../types/TInteger.js';

export function validateInteger(value: any): ValidationFailure[] {
    if (typeof value === 'number' && Number.isInteger(value)) {
        if (value === 9223372036854776000 || value === -9223372036854776000) {
            return [
                new ValidationFailure([], 'NumberOutOfRange', {}),
                new ValidationFailure([], 'NumberTruncated', {}),
            ];
        }
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, integerName);
    }
}
