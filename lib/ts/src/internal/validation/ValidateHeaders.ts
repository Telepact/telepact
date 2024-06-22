import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UFn } from 'uapi/internal/types/UFn';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';

export function validateHeaders(
    headers: Record<string, any>,
    parsedRequestHeaders: Record<string, UFieldDeclaration>,
    functionType: UFn,
): ValidationFailure[] {
    const validationFailures: ValidationFailure[] = [];

    for (const header in headers) {
        const headerValue = headers[header];
        const field = parsedRequestHeaders[header];
        if (field) {
            const thisValidationFailures = field.typeDeclaration.validate(headerValue, null, functionType.name, []);
            const thisValidationFailuresPath = thisValidationFailures.map(
                (e) => new ValidationFailure([header, ...e.path], e.reason, e.data),
            );
            validationFailures.push(...thisValidationFailuresPath);
        }
    }

    return validationFailures;
}
