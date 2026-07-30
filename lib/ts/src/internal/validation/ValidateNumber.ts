//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { numberName } from '../types/TNumber.js';

export function validateNumber(value: any): Array<ValidationFailure> {
    if (typeof value === 'number') {
        if ((Number.isInteger(value) && value === 9223372036854776000) || value === -9223372036854776000) {
            return [
                new ValidationFailure([], 'NumberOutOfRange', {}),
                new ValidationFailure([], 'NumberTruncated', {}),
            ];
        }
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, numberName);
    }
}
