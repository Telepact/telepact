import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { booleanName } from '../../internal/types/UBoolean';

export function validateBoolean(value: any): ValidationFailure[] {
    if (typeof value === 'boolean') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, booleanName);
    }
}
