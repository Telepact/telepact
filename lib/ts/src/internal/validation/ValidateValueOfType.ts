import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { UType } from '../../internal/types/UType';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { UGeneric } from '../../internal/types/UGeneric';

export function validateValueOfType(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    generics: UTypeDeclaration[],
    thisType: UType,
    nullable: boolean,
    typeParameters: UTypeDeclaration[],
): ValidationFailure[] {
    if (value === null) {
        let isNullable = nullable;
        if (thisType instanceof UGeneric) {
            const genericIndex = thisType.index;
            const generic = generics[genericIndex];
            isNullable = generic.nullable;
        }

        if (!isNullable) {
            return getTypeUnexpectedValidationFailure([], value, thisType.getName(generics));
        } else {
            return [];
        }
    }

    return thisType.validate(value, select, fn, typeParameters, generics);
}
