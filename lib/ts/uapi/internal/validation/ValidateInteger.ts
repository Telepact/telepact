import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { get_type_unexpected_validation_failure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { _INTEGER_NAME } from 'uapi/internal/types/UInteger';

export function validateInteger(value: any): ValidationFailure[] {
    if (typeof value === 'number' && !isNaN(value) && !Number.isInteger(value)) {
        if (value > 2 ** 63 - 1 || value < -(2 ** 63)) {
            return [new ValidationFailure([], 'NumberOutOfRange', {})];
        } else {
            return [];
        }
    }

    return get_type_unexpected_validation_failure([], value, _INTEGER_NAME);
}
