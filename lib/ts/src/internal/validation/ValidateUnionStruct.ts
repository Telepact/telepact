import { UStruct } from 'uapi/internal/types/UStruct';
import { UTypeDeclaration } from 'uapi/internal/types/UTypeDeclaration';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { validateStructFields } from 'uapi/internal/validation/ValidateStructFields';

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
