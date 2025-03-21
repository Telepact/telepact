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

import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { structName } from '../types/VStruct';
import { ValidateContext } from './ValidateContext';

export function validateStruct(
    value: any,
    name: string,
    fields: Record<string, VFieldDeclaration>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = ctx.select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, structName);
    }
}
