//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { validateStructFields } from '../../internal/validation/ValidateStructFields.js';
import { structName } from '../types/TStruct.js';
import { ValidateContext } from './ValidateContext.js';

export function validateStruct(
    value: any,
    name: string,
    fields: Record<string, TFieldDeclaration>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = ctx.select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, structName);
    }
}
