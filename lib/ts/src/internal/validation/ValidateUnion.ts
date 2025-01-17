import { UStruct } from '../../internal/types/UStruct';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionCases } from '../../internal/validation/ValidateUnionCases';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { unionName } from '../types/UUnion';
import { ValidateContext } from './ValidateContext';

export function validateUnion(
    value: any,
    name: string,
    cases: Record<string, UStruct>,
    ctx: ValidateContext,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        let selectedCases: Record<string, any>;
        if (name.startsWith('fn.')) {
            selectedCases = { [name]: ctx.select?.[name] ?? null };
        } else {
            selectedCases = ctx.select?.[name] ?? null;
        }
        return validateUnionCases(cases, selectedCases, value, ctx);
    } else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}
