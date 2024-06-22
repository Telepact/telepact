import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { validateUnionCases } from 'uapi/internal/validation/ValidateUnionCases';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { unionName } from '../types/UUnion';

export function validateUnion(
    value: any,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
    generics: UTypeDeclaration[],
    name: string,
    cases: Record<string, UStruct>,
): ValidationFailure[] {
    if (typeof value === 'object' && value !== null) {
        let selectedCases: Record<string, any>;
        if (name.startsWith('fn.')) {
            selectedCases = { [name]: select?.[name] ?? null };
        } else {
            selectedCases = select?.[name] ?? null;
        }
        return validateUnionCases(cases, selectedCases, value, select, fn, typeParameters);
    } else {
        return getTypeUnexpectedValidationFailure([], value, unionName);
    }
}
