//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { stringName } from '../types/TString.js';

export function validateString(value: any): ValidationFailure[] {
    if (typeof value === 'string') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, stringName);
    }
}
