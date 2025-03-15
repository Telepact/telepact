import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { VType } from '../types/VType';
import { VTypeDeclaration } from '../types/VTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidateContext } from './ValidateContext';

export function validateValueOfType(
    value: any,
    thisType: VType,
    nullable: boolean,
    typeParameters: VTypeDeclaration[],
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
