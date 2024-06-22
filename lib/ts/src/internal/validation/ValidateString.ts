import { getTypeUnexpectedValidationFailure } from '../../internal/validation/GetTypeUnexpectedValidationFailure';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { stringName } from '../../internal/types/UString';

export function validateString(value: any): ValidationFailure[] {
    if (typeof value === 'string') {
        return [];
    } else {
        return getTypeUnexpectedValidationFailure([], value, stringName);
    }
}
