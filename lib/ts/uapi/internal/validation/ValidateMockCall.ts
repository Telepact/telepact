import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { UFn } from 'uapi/internal/types/UFn';

export function validateMockCall(
    givenObj: any,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    types: Record<string, UType>,
): ValidationFailure[] {
    if (!(givenObj instanceof Object)) {
        return getTypeUnexpectedValidationFailure([], givenObj, 'Object');
    }

    const givenMap = givenObj;

    const regexString = /^fn\..*$/;

    const keys = Object.keys(givenMap).sort();

    const matches = keys.filter((k) => regexString.test(k));
    if (matches.length !== 1) {
        return [
            new ValidationFailure([], 'ObjectKeyRegexMatchCountUnexpected', {
                regex: regexString.toString(),
                actual: matches.length,
                expected: 1,
                keys,
            }),
        ];
    }

    const functionName = matches[0];
    const functionDef = types[functionName] as UFn;
    const input = givenMap[functionName];

    const functionDefCall = functionDef.call;
    const functionDefName = functionDef.name;
    const functionDefCallCases = functionDefCall.cases;

    const inputFailures = functionDefCallCases[functionDefName].validate(input, select, fn, [], []);

    const inputFailuresWithPath: ValidationFailure[] = [];
    for (const failure of inputFailures) {
        const newPath = [functionName, ...failure.path];

        inputFailuresWithPath.push(new ValidationFailure(newPath, failure.reason, failure.data));
    }

    return inputFailuresWithPath.filter((failure) => failure.reason !== 'RequiredObjectKeyMissing');
}
