import { UUnion } from 'uapi/internal/types/UUnion';
import { ValidationFailure } from 'uapi/internal/validation/ValidationFailure';
import { mapValidationFailuresToInvalidFieldCases } from 'uapi/internal/validation/MapValidationFailuresToInvalidFieldCases';
import { validateResult } from 'uapi/internal/validation/ValidateResult';
import { Message } from 'uapi/Message';

export function getInvalidErrorMessage(
    error: string,
    validationFailures: ValidationFailure[],
    resultUnionType: UUnion,
    responseHeaders: { [key: string]: any },
): Message {
    const validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
    const newErrorResult: { [key: string]: any } = {
        [error]: {
            cases: validationFailureCases,
        },
    };

    validateResult(resultUnionType, newErrorResult);
    return new Message(responseHeaders, newErrorResult);
}
