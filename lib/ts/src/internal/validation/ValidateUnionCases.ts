import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UStruct } from '../../internal/types/UStruct';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionStruct } from '../../internal/validation/ValidateUnionStruct';

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
            new ValidationFailure([], 'ObjectSizeUnexpected', {
                actual: Object.keys(actual).length,
                expected: 1,
            }),
        ];
    }

    const [unionTarget, unionPayload] = Object.entries(actual)[0];

    const referenceStruct = referenceCases[unionTarget];
    if (referenceStruct === undefined) {
        return [new ValidationFailure([unionTarget], 'ObjectKeyDisallowed', {})];
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
