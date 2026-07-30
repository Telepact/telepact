//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { booleanName } from '../types/TBoolean.js';

export function validateBoolean(value: any): ValidationFailure[] {
    if (typeof value === 'boolean') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, booleanName);
    }
}
