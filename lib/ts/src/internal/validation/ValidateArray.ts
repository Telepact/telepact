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

import { VTypeDeclaration } from '../types/VTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { arrayName } from '../types/VArray';
import { ValidateContext } from './ValidateContext';

export function validateArray(
    value: any,
    typeParameters: VTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];

        const validationFailures: ValidationFailure[] = [];
        for (let i = 0; i < value.length; i++) {
            const element = value[i];
            const nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);
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
