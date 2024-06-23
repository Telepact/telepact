import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { structName } from '../../internal/types/UStruct';

export function validateStruct(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    name: string,
    fields: Record<string, UFieldDeclaration>,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, select, fn, typeParameters);
    } else {
        return getTypeUnexpectedValidationFailure([], value, structName);
    }
}
