import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { structName } from '../../internal/types/UStruct';
import { ValidateContext } from './ValidateContext';

export function validateStruct(
    value: any,
    name: string,
    fields: Record<string, UFieldDeclaration>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = ctx.select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, structName);
    }
}
