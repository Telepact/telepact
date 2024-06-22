import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from 'uapi/internal/validation/GetTypeUnexpectedValidationFailure';
import { integerName } from 'uapi/internal/types/UInteger';

export function validateInteger(value: any): ValidationFailure[] {
    if (typeof value === 'number' && Number.isInteger(value)) {
        if (value === 9223372036854776000 || value === -9223372036854776000) {
            return [
                new ValidationFailure([], 'NumberOutOfRange', {}),
                new ValidationFailure([], 'NumberTruncated', {}),
            ];
        }
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, integerName);
    }
}
