import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { VStruct } from '../types/VStruct';
import { VType } from '../types/VType';
import { VUnion } from '../types/VUnion';
import { VFn } from '../types/VFn';
import { ValidateContext } from './ValidateContext';

export function validateMockStub(
    givenObj: any,
    types: { [key: string]: VType },
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
    const functionDef = types[functionName] as VFn;
    const input = givenMap[functionName];

    const functionDefCall: VUnion = functionDef.call;
    const functionDefName: string = functionDef.name;
    const functionDefCallTags: { [key: string]: VStruct } = functionDefCall.tags;
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
