import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { get_type_unexpected_validation_failure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { _BOOLEAN_NAME } from 'uapi/internal/types/UBoolean';

export function validateBoolean(value: any): ValidationFailure[] {
    if (typeof value === 'boolean') {
        return [];
    } else {
        return get_type_unexpected_validation_failure([], value, _BOOLEAN_NAME);
    }
}
