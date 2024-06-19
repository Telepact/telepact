import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { objectName } from 'uapi/internal/types/UObject';

export function validateObject(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
): ValidationFailure[] {
    if (typeof value === 'object' && value !== null) {
        const nestedTypeDeclaration = typeParameters[0];

        const validationFailures: ValidationFailure[] = [];
        for (const [k, v] of Object.entries(value)) {
            const nestedValidationFailures = nestedTypeDeclaration.validate(v, select, fn, generics);

            const nestedValidationFailuresWithPath: ValidationFailure[] = [];
            for (const f of nestedValidationFailures) {
                const thisPath = [k, ...f.path];

                nestedValidationFailuresWithPath.push(new ValidationFailure(thisPath, f.reason, f.data));
            }

            validationFailures.push(...nestedValidationFailuresWithPath);
        }

        return validationFailures;
    } else {
        return getTypeUnexpectedValidationFailure([], value, objectName);
    }
}
