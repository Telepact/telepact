//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TUnion } from '../types/TUnion.js';
import { TelepactError } from '../../TelepactError.js';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases.js';
import { ValidateContext } from './ValidateContext.js';

export function validateResult(resultUnionType: TUnion, errorResult: any): void {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, [], new ValidateContext(null, null, false));
    if (newErrorResultValidationFailures.length !== 0) {
        throw new TelepactError(
            `Failed internal telepact validation: ${JSON.stringify(mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures))}`,
        );
    }
}
