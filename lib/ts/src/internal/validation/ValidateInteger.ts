import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { integerName } from '../types/VInteger';

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
