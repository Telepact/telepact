//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { ValidateContext } from './ValidateContext.js';

export function validateHeaders(
    headers: Record<string, any>,
    parsedRequestHeaders: Record<string, TFieldDeclaration>,
    functionName: string,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    for (const header in headers) {
        const headerValue = headers[header];
        const field = parsedRequestHeaders[header];

        if (!header.startsWith("@")) {
            validationFailures.push(new ValidationFailure([header], "RequiredObjectKeyPrefixMissing", {"prefix": "@"}));
        }

        if (field) {
            const thisValidationFailures = field.typeDeclaration.validate(
                headerValue,
                new ValidateContext(null, functionName, false),
            );
            const thisValidationFailuresPath = thisValidationFailures.map(
                (e) => new ValidationFailure([header, ...e.path], e.reason, e.data),
            );
            validationFailures.push(...thisValidationFailuresPath);
        }
    }

    return validationFailures;
}
