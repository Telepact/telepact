import { UStruct } from '../../internal/types/UStruct';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { ValidateContext } from './ValidateContext';

export function validateUnionStruct(
    unionStruct: UStruct,
    unionCase: string,
    actual: Record<string, any>,
    selectedCases: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    const selectedFields = (selectedCases?.[unionCase] as string[] | undefined) ?? null;

    return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
}
