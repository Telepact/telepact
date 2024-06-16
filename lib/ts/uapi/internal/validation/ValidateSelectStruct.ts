import { UStruct } from 'uapi/internal/types/UStruct';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';

export function validateSelectStruct(
    structReference: UStruct,
    basePath: any[],
    selectedFields: any,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    if (!Array.isArray(selectedFields)) {
        return getTypeUnexpectedValidationFailure(basePath, selectedFields, 'Array');
    }

    const fields = selectedFields;

    for (let i = 0; i < fields.length; i++) {
        const field = fields[i];

        if (typeof field !== 'string') {
            const thisPath = [...basePath, i];
            validationFailures.push(getTypeUnexpectedValidationFailure(thisPath, field, 'String'));
            continue;
        }

        const stringField = field;

        if (!(stringField in structReference.fields)) {
            const thisPath = [...basePath, i];
            validationFailures.push(new ValidationFailure(thisPath, 'ObjectKeyDisallowed', {}));
        }
    }

    return validationFailures;
}
