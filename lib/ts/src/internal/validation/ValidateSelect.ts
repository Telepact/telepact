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

import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidateContext } from './ValidateContext';

export function validateSelect(
    givenObj: any,
    possibleFnSelects: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof givenObj !== 'object' || Array.isArray(givenObj) || givenObj === null || givenObj === undefined) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const possibleSelect = possibleFnSelects[ctx.fn] as Record<string, any>;

    return isSubSelect([], givenObj, possibleSelect);
}

function isSubSelect(path: any[], givenObj: any, possibleSelectSection: any): ValidationFailure[] {
    if (Array.isArray(possibleSelectSection)) {
        if (!Array.isArray(givenObj)) {
            return getTypeUnexpectedValidationFailure(path, givenObj, 'Array');
        }

        const validationFailures: ValidationFailure[] = [];

        for (const [index, element] of givenObj.entries()) {
            if (!possibleSelectSection.includes(element)) {
                validationFailures.push(new ValidationFailure([...path, index], 'ArrayElementDisallowed', {}));
            }
        }

        return validationFailures;
    } else if (typeof possibleSelectSection === 'object' && !Array.isArray(possibleSelectSection)) {
        if (typeof givenObj !== 'object' || Array.isArray(givenObj) || givenObj === null) {
            return getTypeUnexpectedValidationFailure(path, givenObj, 'Object');
        }

        const validationFailures: ValidationFailure[] = [];

        for (const [key, value] of Object.entries(givenObj)) {
            if (key in possibleSelectSection) {
                const innerFailures = isSubSelect([...path, key], value, possibleSelectSection[key]);
                validationFailures.push(...innerFailures);
            } else {
                validationFailures.push(new ValidationFailure([...path, key], 'ObjectKeyDisallowed', {}));
            }
        }

        return validationFailures;
    }

    return [];
}
