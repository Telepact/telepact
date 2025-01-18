import { UUnion } from '../../internal/types/UUnion';
import { UApiError } from '../../UApiError';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases';
import { ValidateContext } from './ValidateContext';

export function validateResult(resultUnionType: UUnion, errorResult: any): void {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, [], new ValidateContext(null, null));
    if (newErrorResultValidationFailures.length !== 0) {
        throw new UApiError(
            `Failed internal uAPI validation: ${JSON.stringify(mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures))}`,
        );
    }
}
