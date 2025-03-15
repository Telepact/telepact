import { VTypeDeclaration } from '../types/VTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { arrayName } from '../types/VArray';
import { ValidateContext } from './ValidateContext';

export function validateArray(
    value: any,
    typeParameters: VTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (Array.isArray(value)) {
        const nestedTypeDeclaration = typeParameters[0];

        const validationFailures: ValidationFailure[] = [];
        for (let i = 0; i < value.length; i++) {
            const element = value[i];
            const nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);
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
        return getTypeUnexpectedValidationFailure([], value, arrayName);
    }
}
