import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';

export function validateValueOfType(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    thisType: UType,
    nullable: boolean,
    typeParameters: UTypeDeclaration[],
): ValidationFailure[] {
    if (value === null) {
        if (!nullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName());
        } else {
            return [];
        }
    }

    return thisType.validate(value, select, fn, typeParameters);
}
