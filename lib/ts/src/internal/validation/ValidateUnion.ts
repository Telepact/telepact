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

import { TStruct } from '../types/TStruct';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionTags } from '../../internal/validation/ValidateUnionTags';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { unionName } from '../types/TUnion';
import { ValidateContext } from './ValidateContext';

export function validateUnion(
    value: any,
    name: string,
    tags: Record<string, TStruct>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        let selectedTags: Record<string, any>;
        if (name.startsWith('fn.')) {
            selectedTags = { [name]: ctx.select?.[name] ?? null };
        } else {
            selectedTags = ctx.select?.[name] ?? null;
        }
        return validateUnionTags(tags, selectedTags, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}
