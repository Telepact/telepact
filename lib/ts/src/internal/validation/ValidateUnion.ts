import { UStruct } from '../../internal/types/UStruct';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionCases } from '../../internal/validation/ValidateUnionCases';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { unionName } from '../types/UUnion';

export function validateUnion(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    name: string,
    cases: Record<string, UStruct>,
): ValidationFailure[] {
    if (typeof value === 'object' && !Array.isArray(value)) {
        let selectedCases: Record<string, any>;
        if (name.startsWith('fn.')) {
            selectedCases = { [name]: select?.[name] ?? null };
        } else {
            selectedCases = select?.[name] ?? null;
        }
        return validateUnionCases(cases, selectedCases, value, select, fn);
    } else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}
