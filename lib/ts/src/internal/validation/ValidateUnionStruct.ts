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
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { ValidateContext } from './ValidateContext';

export function validateUnionStruct(
    unionStruct: TStruct,
    unionTag: string,
    actual: Record<string, any>,
    selectedTags: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    const selectedFields = (selectedTags?.[unionTag] as string[] | undefined) ?? null;

    return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
}
