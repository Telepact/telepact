import { UStruct } from '../../internal/types/UStruct';
import { UTypeDeclaration } from '../../internal/types/UTypeDeclaration';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { validateStructFields } from '../../internal/validation/ValidateStructFields';

export function validateUnionStruct(
    unionStruct: UStruct,
    unionCase: string,
    actual: Record<string, any>,
    selectedCases: Record<string, any>,
    select: Record<string, any> | null,
    fn: string | null,
    typeParameters: UTypeDeclaration[],
): ValidationFailure[] {
    const selectedFields = selectedCases?.[unionCase] as string[] | undefined;

    return validateStructFields(unionStruct.fields, selectedFields, actual, select, fn, typeParameters);
}
