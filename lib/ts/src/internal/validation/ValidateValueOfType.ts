import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidateContext } from './ValidateContext';

export function validateValueOfType(
    value: any,
    thisType: UType,
    nullable: boolean,
    typeParameters: UTypeDeclaration[],
    ctx: ValidateContext,
): ValidationFailure[] {
    if (value === null) {
        if (!nullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName());
        } else {
            return [];
        }
    }

    return thisType.validate(value, typeParameters, ctx);
}
