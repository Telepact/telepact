import { VFieldDeclaration } from '../types/VFieldDeclaration';
import { VFn } from '../types/VFn';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { ValidateContext } from './ValidateContext';

export function validateHeaders(
    headers: Record<string, any>,
    parsedRequestHeaders: Record<string, VFieldDeclaration>,
    functionType: VFn,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    for (const header in headers) {
        const headerValue = headers[header];
        const field = parsedRequestHeaders[header];
        if (field) {
            const thisValidationFailures = field.typeDeclaration.validate(
                headerValue,
                new ValidateContext(null, functionType.name),
            );
            const thisValidationFailuresPath = thisValidationFailures.map(
                (e) => new ValidationFailure([header, ...e.path], e.reason, e.data),
            );
            validationFailures.push(...thisValidationFailuresPath);
        }
    }

    return validationFailures;
}
