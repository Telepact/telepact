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
import { TStruct } from '../types/TStruct';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionStruct } from '../../internal/validation/ValidateUnionStruct';
import { ValidateContext } from './ValidateContext';

export function validateUnionTags(
    referenceTags: Record<string, TStruct>,
    selectedTags: Record<string, any>,
    actual: Record<any, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (Object.keys(actual).length !== 1) {
        return [
            new ValidationFailure([], 'ObjectSizeUnexpected', {
                actual: Object.keys(actual).length,
                expected: 1,
            }),
        ];
    }

    const [unionTarget, unionPayload] = Object.entries(actual)[0];

    const referenceStruct = referenceTags[unionTarget];
    if (referenceStruct === undefined) {
        return [new ValidationFailure([unionTarget], 'ObjectKeyDisallowed', {})];
    }

    if (typeof unionPayload === 'object' && !Array.isArray(unionPayload)) {
        const nestedValidationFailures = validateUnionStruct(
            referenceStruct,
            unionTarget,
            unionPayload,
            selectedTags,
            ctx,
        );

        const nestedValidationFailuresWithPath: ValidationFailure[] = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [unionTarget, ...failure.path];
            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }

        return nestedValidationFailuresWithPath;
    } else {
        return getTypeUnexpectedValidationFailure([unionTarget], unionPayload, 'Object');
    }
}
