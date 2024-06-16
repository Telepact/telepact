import { UUnion } from 'uapi/internal/types/UUnion';
import { UApiError } from 'uapi/UApiError';
import { mapValidationFailuresToInvalidFieldCases } from 'uapi/internal/validation/MapValidationFailuresToInvalidFieldCases';

export function validateResult(resultUnionType: UUnion, errorResult: any): void {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, null, null, [], []);
    if (newErrorResultValidationFailures) {
        throw new UApiError(
            `Failed internal uAPI validation: ${mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures)}`,
        );
    }
}
