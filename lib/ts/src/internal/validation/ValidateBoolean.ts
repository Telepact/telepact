import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { booleanName } from 'uapi/internal/types/UBoolean';

export function validateBoolean(value: any): ValidationFailure[] {
    if (typeof value === 'boolean') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, booleanName);
    }
}
