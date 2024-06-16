import { get_type_unexpected_validation_failure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { _NUMBER_NAME } from 'uapi/internal/types/UNumber';

export function validateNumber(value: any): ValidationFailure[] {
    if (typeof value === 'number' && !isNaN(value) && !isNaN(parseFloat(value))) {
        if (Number.isInteger(value)) {
            if (value > 2 ** 63 - 1 || value < -(2 ** 63)) {
                return [new ValidationFailure([], 'NumberOutOfRange', {})];
            } else {
                return [];
            }
        } else {
            return [];
        }
    } else {
        return get_type_unexpected_validation_failure([], value, _NUMBER_NAME);
    }
}
