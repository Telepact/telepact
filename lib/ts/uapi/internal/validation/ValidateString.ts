import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { _STRING_NAME } from 'uapi/internal/types/UString';

export function validateString(value: any): ValidationFailure[] {
    if (typeof value === 'string') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, _STRING_NAME);
    }
}
