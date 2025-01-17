import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { objectName } from '../../internal/types/UObject';
import { ValidateContext } from './ValidateContext';

export function validateObject(
    value: any,
    typeParameters: UTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];

        const validationFailures: ValidationFailure[] = [];
        for (const [k, v] of Object.entries(value)) {
            const nestedValidationFailures = nestedTypeDeclaration.validate(v, ctx);

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
