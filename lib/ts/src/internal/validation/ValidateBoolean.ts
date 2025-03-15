import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { booleanName } from '../types/VBoolean';

export function validateBoolean(value: any): ValidationFailure[] {
    if (typeof value === 'boolean') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, booleanName);
    }
}
