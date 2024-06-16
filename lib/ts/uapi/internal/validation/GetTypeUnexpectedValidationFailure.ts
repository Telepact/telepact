import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { getType } from 'uapi/internal/types/GetType';

export function getTypeUnexpectedValidationFailure(path: any[], value: any, expectedType: string): ValidationFailure[] {
    const actualType = getType(value);
    const data: { [key: string]: any } = {
        actual: { [actualType]: {} },
        expected: { [expectedType]: {} },
    };
    return [new ValidationFailure(path, 'TypeUnexpected', data)];
}
