import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { numberName } from '../../internal/types/UNumber';

export function validateNumber(value: any): Array<ValidationFailure> {
    if (typeof value === 'number') {
        if ((Number.isInteger(value) && value === 9223372036854776000) || value === -9223372036854776000) {
            return [
                new ValidationFailure([], 'NumberOutOfRange', {}),
                new ValidationFailure([], 'NumberTruncated', {}),
            ];
        }
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, numberName);
    }
}
