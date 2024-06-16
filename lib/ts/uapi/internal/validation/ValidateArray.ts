import { TYPE_CHECKING } from 'typing';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';

export function validateArray(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
): ValidationFailure[] {
    if (TYPE_CHECKING) {
        // Add type checking related code here
    }

    if (Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];

        const validationFailures: ValidationFailure[] = [];
        for (let i = 0; i < value.length; i++) {
            const element = value[i];
            const nestedValidationFailures = nestedTypeDeclaration.validate(element, select, fn, generics);
            const index = i;

            const nestedValidationFailuresWithPath: ValidationFailure[] = [];
            for (const f of nestedValidationFailures) {
                const finalPath = [index, ...f.path];

                nestedValidationFailuresWithPath.push(new ValidationFailure(finalPath, f.reason, f.data));
            }

            validationFailures.push(...nestedValidationFailuresWithPath);
        }

        return validationFailures;
    } else {
        return getTypeUnexpectedValidationFailure([], value, _ARRAY_NAME);
    }
}
