import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { validateStructFields } from 'uapi/internal/validation/ValidateStructFields';
import { STRUCT_NAME } from 'uapi/internal/types/UStruct';

export function validateStruct(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    name: string,
    fields: Record<string, UFieldDeclaration>,
): ValidationFailure[] {
    if (typeof value === 'object' && value !== null) {
        const selectedFields = select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, select, fn, typeParameters);
    } else {
        return getTypeUnexpectedValidationFailure([], value, STRUCT_NAME);
    }
}
