import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { UStruct } from '../../internal/types/UStruct';
import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { UUnion } from '../../internal/types/UUnion';
import { UFn } from '../../internal/types/UFn';

export function validateMockStub(
    givenObj: any,
    select: { [key: string]: any } | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    types: { [key: string]: UType },
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
                regex: regexString,
                actual: matches.length,
                expected: 1,
                keys: keys,
            }),
        ];
    }

    const functionName = matches[0];
    const functionDef = types[functionName] as UFn;
    const input = givenMap[functionName];

    const functionDefCall: UUnion = functionDef.call;
    const functionDefName: string = functionDef.name;
    const functionDefCallCases: { [key: string]: UStruct } = functionDefCall.cases;
    const inputFailures = functionDefCallCases[functionDefName].validate(input, select, fn, [], []);

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
        validationFailures.push(new ValidationFailure([resultDefKey], 'RequiredObjectKeyMissing', {}));
    } else {
        const output = givenMap[resultDefKey];
        const outputFailures = functionDef.result.validate(output, select, fn, [], []);

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
