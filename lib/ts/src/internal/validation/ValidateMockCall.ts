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
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { TFn } from '../types/TFn';
import { ValidateContext } from './ValidateContext';

export function validateMockCall(
    givenObj: any,
    types: Record<string, TType>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (!(typeof givenObj === 'object' && !Array.isArray(givenObj))) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const givenMap = givenObj;

    const regexString = /^fn\..*$/;

    const keys = Object.keys(givenMap).sort();

    const matches = keys.filter((k) => regexString.test(k));
    if (matches.length !== 1) {
        return [
            new ValidationFailure([], 'ObjectKeyRegexMatchCountUnexpected', {
                regex: regexString.toString().slice(1, -1),
                actual: matches.length,
                expected: 1,
                keys,
            }),
        ];
    }

    const functionName = matches[0];
    const functionDef = types[functionName] as TFn;
    const input = givenMap[functionName];

    const functionDefCall = functionDef.call;
    const functionDefName = functionDef.name;
    const functionDefCallTags = functionDefCall.tags;

    const inputFailures = functionDefCallTags[functionDefName].validate(input, [], ctx);

    const inputFailuresWithPath: ValidationFailure[] = [];
    for (const failure of inputFailures) {
        const newPath = [functionName, ...failure.path];

        inputFailuresWithPath.push(new ValidationFailure(newPath, failure.reason, failure.data));
    }

    return inputFailuresWithPath.filter((failure) => failure.reason !== 'RequiredObjectKeyMissing');
}
