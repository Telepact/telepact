//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure.js';
import { arrayName } from '../types/TArray.js';
import { ValidateContext } from './ValidateContext.js';

export function validateArray(
    value: any,
    typeParameters: TTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];

        const validationFailures: ValidationFailure[] = [];
        for (let i = 0; i < value.length; i++) {
            const element = value[i];

            ctx.path.push("*");

            const nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);

            ctx.path.pop();

            const index = i;

            const nestedValidationFailuresWithPath: ValidationFailure[] = [];
            for (const f of nestedValidationFailures) {
                const finalPath = [index, ...f.path];

                nestedValidationFailuresWithPath.push(new ValidationFailure(finalPath, f.reason, f.data));
            }

            validationFailures.push(...nestedValidationFailuresWithPath);
        }

        return validationFailures;
    } else {
        return getTypeUnexpectedValidationFailure([], value, arrayName);
    }
}
