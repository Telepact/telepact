//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TStruct } from '../types/TStruct.js';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { validateUnionTags } from '../../internal/validation/ValidateUnionTags.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { unionName } from '../types/TUnion.js';
import { ValidateContext } from './ValidateContext.js';

export function validateUnion(
    value: any,
    name: string,
    tags: Record<string, TStruct>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        let selectedTags: Record<string, any>;
        if (name.startsWith('fn.')) {
            selectedTags = { [name]: ctx.select?.[name] ?? null };
        } else {
            selectedTags = ctx.select?.[name] ?? null;
        }
        return validateUnionTags(tags, selectedTags, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}
