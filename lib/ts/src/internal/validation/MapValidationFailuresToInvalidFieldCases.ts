//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';

export function mapValidationFailuresToInvalidFieldCases(
    argumentValidationFailures: ValidationFailure[],
): Record<string, any>[] {
    const validationFailureCases: Record<string, any>[] = [];
    for (const validationFailure of argumentValidationFailures) {
        const validationFailureCase = {
            path: validationFailure.path,
            reason: { [validationFailure.reason]: validationFailure.data },
        };
        validationFailureCases.push(validationFailureCase);
    }

    return validationFailureCases;
}
