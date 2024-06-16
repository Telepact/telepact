import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';

export function mapValidationFailuresToInvalidFieldCases(
    argumentValidationFailures: ValidationFailure[],
): { path: string; reason: { [key: string]: any } }[] {
    const validationFailureCases: { path: string; reason: { [key: string]: any } }[] = [];
    for (const validationFailure of argumentValidationFailures) {
        const validationFailureCase: { path: string; reason: { [key: string]: any } } = {
            path: validationFailure.path,
            reason: { [validationFailure.reason]: validationFailure.data },
        };
        validationFailureCases.push(validationFailureCase);
    }

    return validationFailureCases;
}
