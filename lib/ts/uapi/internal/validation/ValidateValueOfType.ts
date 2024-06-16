import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { UType } from 'uapi/internal/types/UType';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { UGeneric } from 'uapi/internal/types/UGeneric';

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
            return [getTypeUnexpectedValidationFailure([], value, thisType.getName(generics))];
        } else {
            return [];
        }
    }

    return thisType.validate(value, select, fn, typeParameters, generics);
}
