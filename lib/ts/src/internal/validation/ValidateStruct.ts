import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { structName } from '../types/VStruct';
import { ValidateContext } from './ValidateContext';

export function validateStruct(
    value: any,
    name: string,
    fields: Record<string, VFieldDeclaration>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        const selectedFields = ctx.select?.[name] ?? null;
        return validateStructFields(fields, selectedFields, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, structName);
    }
}
