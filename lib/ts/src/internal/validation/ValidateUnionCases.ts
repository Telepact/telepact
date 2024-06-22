import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionStruct } from 'uapi/internal/validation/ValidateUnionStruct';

export function validateUnionCases(
    referenceCases: Record<string, UStruct>,
    selectedCases: Record<string, any>,
    actual: Record<any, any>,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
): ValidationFailure[] {
    if (Object.keys(actual).length !== 1) {
        return [
            new ValidationFailure([], 'objectSizeUnexpected', {
                actual: Object.keys(actual).length,
                expected: 1,
            }),
        ];
    }

    const [unionTarget, unionPayload] = Object.entries(actual)[0];

    const referenceStruct = referenceCases[unionTarget];
    if (!referenceStruct) {
        return [new ValidationFailure([unionTarget], 'objectKeyDisallowed', {})];
    }

    if (typeof unionPayload === 'object') {
        const nestedValidationFailures = validateUnionStruct(
            referenceStruct,
            unionTarget,
            unionPayload,
            selectedCases,
            select,
            fn,
            typeParameters,
        );

        const nestedValidationFailuresWithPath: ValidationFailure[] = [];
        for (const failure of nestedValidationFailures) {
            const thisPath = [unionTarget, ...failure.path];
            nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, failure.reason, failure.data));
        }

        return nestedValidationFailuresWithPath;
    } else {
        return getTypeUnexpectedValidationFailure([unionTarget], unionPayload, 'object');
    }
}
