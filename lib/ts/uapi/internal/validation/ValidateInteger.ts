import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { integerName } from 'uapi/internal/types/UInteger';

export function validateInteger(value: any): ValidationFailure[] {
    if (typeof value === 'number' && !isNaN(value) && !Number.isInteger(value)) {
        if (value > 2 ** 63 - 1 || value < -(2 ** 63)) {
            return [new ValidationFailure([], 'NumberOutOfRange', {})];
        } else {
            return [];
        }
    }

    return getTypeUnexpectedValidationFailure([], value, integerName);
}
