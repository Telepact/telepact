//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { VUnion } from '../types/VUnion';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases';
import { validateResult } from '../../internal/validation/ValidateResult';
import { Message } from '../../Message';

export function getInvalidErrorMessage(
    error: string,
    validationFailures: ValidationFailure[],
    resultUnionType: VUnion,
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
