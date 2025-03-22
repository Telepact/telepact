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
import { TType } from '../types/TType';
import { TTypeDeclaration } from '../types/TTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidateContext } from './ValidateContext';

export function validateValueOfType(
    value: any,
    thisType: TType,
    nullable: boolean,
    typeParameters: TTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (value === null) {
        if (!nullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName());
        } else {
            return [];
        }
    }

    return thisType.validate(value, typeParameters, ctx);
}
