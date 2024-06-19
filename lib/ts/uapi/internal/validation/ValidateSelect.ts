import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { UType } from 'uapi/internal/types/UType';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { validateSelectStruct } from 'uapi/internal/validation/ValidateSelectStruct';
import { UUnion } from 'uapi/internal/types/UUnion';
import { UFn } from 'uapi/internal/types/UFn';
import { UStruct } from 'uapi/internal/types/UStruct';

export function validateSelect(
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

    const selectStructFieldsHeader = givenObj;

    const validationFailures: ValidationFailure[] = [];
    const functionType = types[fn as string] as UFn;

    for (const [type, selectValue] of Object.entries(selectStructFieldsHeader)) {
        let typeReference: UType;
        if (type === '->') {
            typeReference = functionType.result;
        } else {
            const possibleTypeReference = types[type];
            if (possibleTypeReference === undefined) {
                validationFailures.push(new ValidationFailure([type], 'ObjectKeyDisallowed', {}));
                continue;
            }

            typeReference = possibleTypeReference;
        }

        if (typeReference instanceof UUnion) {
            const u = typeReference;
            if (!(selectValue instanceof Object)) {
                validationFailures.push(...getTypeUnexpectedValidationFailure([type], selectValue, 'Object'));
                continue;
            }

            const unionCases = selectValue;

            for (const [unionCase, selectedCaseStructFields] of Object.entries(unionCases)) {
                const structRef = u.cases[unionCase];

                const loopPath = [type, unionCase];

                if (structRef === undefined) {
                    validationFailures.push(new ValidationFailure(loopPath, 'ObjectKeyDisallowed', {}));
                    continue;
                }

                const nestedValidationFailures = validateSelectStruct(structRef, loopPath, selectedCaseStructFields);

                validationFailures.push(...nestedValidationFailures);
            }
        } else if (typeReference instanceof UFn) {
            const f = typeReference;
            const fnCall = f.call;
            const fnCallCases = fnCall.cases;
            const fnName = f.name;
            const argStruct = fnCallCases[fnName];
            const nestedValidationFailures = validateSelectStruct(argStruct, [type], selectValue);

            validationFailures.push(...nestedValidationFailures);
        } else if (typeReference instanceof UStruct) {
            const structRef = typeReference;
            const nestedValidationFailures = validateSelectStruct(structRef, [type], selectValue);

            validationFailures.push(...nestedValidationFailures);
        } else {
            validationFailures.push(new ValidationFailure([type], 'ObjectKeyDisallowed', {}));
        }
    }

    return validationFailures;
}
