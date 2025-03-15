import { VStruct } from '../types/VStruct';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';
import { ValidateContext } from './ValidateContext';

export function validateUnionStruct(
    unionStruct: VStruct,
    unionTag: string,
    actual: Record<string, any>,
    selectedTags: Record<string, any>,
    ctx: ValidateContext,
): ValidationFailure[] {
    const selectedFields = (selectedTags?.[unionTag] as string[] | undefined) ?? null;

    return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
}
