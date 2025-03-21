import { VUnion } from '../types/VUnion';
import { TelepactError } from '../../TelepactError';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases';
import { ValidateContext } from './ValidateContext';

export function validateResult(resultUnionType: VUnion, errorResult: any): void {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, [], new ValidateContext(null, null));
    if (newErrorResultValidationFailures.length !== 0) {
        throw new TelepactError(
            `Failed internal telepact validation: ${JSON.stringify(mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures))}`,
        );
    }
}
