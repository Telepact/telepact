import { UUnion } from '../../internal/types/UUnion';
import { ValidationFailure } from '../../internal/validation/ValidationFailure';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases';
import { validateResult } from '../../internal/validation/ValidateResult';
import { Message } from '../../Message';

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
