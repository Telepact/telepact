//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TUnion } from '../types/TUnion.js';
import { ValidationFailure } from '../../internal/validation/ValidationFailure.js';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases.js';
import { validateResult } from '../../internal/validation/ValidateResult.js';
import { Message } from '../../Message.js';

export function getInvalidErrorMessage(
    error: string,
    validationFailures: ValidationFailure[],
    resultUnionType: TUnion,
    responseHeaders: { [key: string]: any },
): Message {
    const validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
    const newErrorResult: { [key: string]: any } = {
        [error]: {
            cases: validationFailureCases,
        },
    };

    validateResult(resultUnionType, newErrorResult);
    return new Message(responseHeaders, newErrorResult);
}
