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
import { TStruct } from '../types/TStruct';
import { TType } from '../types/TType';
import { TUnion } from '../types/TUnion';
import { TFn } from '../types/TFn';
import { ValidateContext } from './ValidateContext';

export function validateMockStub(
    givenObj: any,
    types: { [key: string]: TType },
    ctx: ValidateContext,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    if (!(typeof givenObj === 'object' && !Array.isArray(givenObj))) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const givenMap: { [key: string]: any } = givenObj;

    const regexString = /^fn\..*$/;

    const keys = Object.keys(givenMap).sort();

    const matches = keys.filter((k) => regexString.test(k));
    if (matches.length !== 1) {
        return [
            new ValidationFailure([], 'ObjectKeyRegexMatchCountUnexpected', {
                regex: regexString.toString().slice(1, -1),
                actual: matches.length,
                expected: 1,
                keys: keys,
            }),
        ];
    }

    const functionName = matches[0];
    const functionDef = types[functionName] as TFn;
    const input = givenMap[functionName];

    const functionDefCall: TUnion = functionDef.call;
    const functionDefName: string = functionDef.name;
    const functionDefCallTags: { [key: string]: TStruct } = functionDefCall.tags;
    const inputFailures = functionDefCallTags[functionDefName].validate(input, [], ctx);

    const inputFailuresWithPath: ValidationFailure[] = [];
    for (const f of inputFailures) {
        const thisPath = [functionName, ...f.path];

        inputFailuresWithPath.push(new ValidationFailure(thisPath, f.reason, f.data));
    }

    const inputFailuresWithoutMissingRequired = inputFailuresWithPath.filter(
        (f) => f.reason !== 'RequiredObjectKeyMissing',
    );

    validationFailures.push(...inputFailuresWithoutMissingRequired);

    const resultDefKey = '->';

    if (!(resultDefKey in givenMap)) {
        validationFailures.push(new ValidationFailure([], 'RequiredObjectKeyMissing', { key: resultDefKey }));
    } else {
        const output = givenMap[resultDefKey];
        const outputFailures = functionDef.result.validate(output, [], ctx);

        const outputFailuresWithPath: ValidationFailure[] = [];
        for (const f of outputFailures) {
            const thisPath = [resultDefKey, ...f.path];

            outputFailuresWithPath.push(new ValidationFailure(thisPath, f.reason, f.data));
        }

        const failuresWithoutMissingRequired = outputFailuresWithPath.filter(
            (f) => f.reason !== 'RequiredObjectKeyMissing',
        );

        validationFailures.push(...failuresWithoutMissingRequired);
    }

    const disallowedFields = Object.keys(givenMap).filter((k) => !matches.includes(k) && k !== resultDefKey);
    for (const disallowedField of disallowedFields) {
        validationFailures.push(new ValidationFailure([disallowedField], 'ObjectKeyDisallowed', {}));
    }

    return validationFailures;
}
