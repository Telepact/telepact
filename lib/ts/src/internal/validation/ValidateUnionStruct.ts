//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TStruct } from '../types/TStruct.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { validateStructFields } from '../../internal/validation/ValidateStructFields.js';
import { ValidateContext } from './ValidateContext.js';

export function validateUnionStruct(
    unionStruct: TStruct,
    unionTag: string,
    actual: Record<string, any>,
    selectedTags: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    const selectedFields = (selectedTags?.[unionTag] as string[] | undefined) ?? null;

    ctx.path.push(unionTag);

    const result = validateStructFields(unionStruct.fields, selectedFields, actual, ctx);

    ctx.path.pop();

    return result;
}
