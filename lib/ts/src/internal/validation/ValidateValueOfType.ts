//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { TType } from '../types/TType.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { ValidateContext } from './ValidateContext.js';

export function validateValueOfType(
    value: any,
    thisType: TType,
    nullable: boolean,
    typeParameters: TTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (value === null) {
        if (!nullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName());
        } else {
            return [];
        }
    }

    return thisType.validate(value, typeParameters, ctx);
}
