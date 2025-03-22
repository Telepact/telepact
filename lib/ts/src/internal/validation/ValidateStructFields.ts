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
import { TFieldDeclaration } from '../types/TFieldDeclaration';
import { ValidateContext } from './ValidateContext';

export function validateStructFields(
    fields: Record<string, TFieldDeclaration>,
    selectedFields: string[] | null,
    actualStruct: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    const missingFields: string[] = [];
    for (const [fieldName, fieldDeclaration] of Object.entries(fields)) {
        const isOptional = fieldDeclaration.optional;
        const isOmittedBySelect = selectedFields !== null && !selectedFields.includes(fieldName);
        if (!(fieldName in actualStruct) && !isOptional && !isOmittedBySelect) {
            missingFields.push(fieldName);
        }
    }

    for (const missingField of missingFields) {
        const validationFailure = new ValidationFailure([], 'RequiredObjectKeyMissing', {
            key: missingField,
        });

        validationFailures.push(validationFailure);
    }

    for (const [fieldName, fieldValue] of Object.entries(actualStruct)) {
        const referenceField = fields[fieldName];
        if (referenceField === undefined) {
            const validationFailure = new ValidationFailure([fieldName], 'ObjectKeyDisallowed', {});

            validationFailures.push(validationFailure);
            continue;
        }

        const refFieldTypeDeclaration = referenceField.typeDeclaration;

        const nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, ctx);

        const nestedValidationFailuresWithPath: ValidationFailure[] = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [fieldName, ...failure.path];

            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }

        validationFailures.push(...nestedValidationFailuresWithPath);
    }

    return validationFailures;
}
