import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';

export function mapValidationFailuresToInvalidFieldCases(
    argumentValidationFailures: ValidationFailure[],
): Record<string, any>[] {
    const validationFailureCases: Record<string, any>[] = [];
    for (const validationFailure of argumentValidationFailures) {
        const validationFailureCase = {
            path: validationFailure.path,
            reason: { [validationFailure.reason]: validationFailure.data },
        };
        validationFailureCases.push(validationFailureCase);
    }

    return validationFailureCases;
}
