import { VUnion } from '../types/VUnion';
import { MsgPactError } from '../../MsgPactError';
import { mapValidationFailuresToInvalidFieldCases } from '../../internal/validation/MapValidationFailuresToInvalidFieldCases';
import { ValidateContext } from './ValidateContext';

export function validateResult(resultUnionType: VUnion, errorResult: any): void {
    const newErrorResultValidationFailures = resultUnionType.validate(errorResult, [], new ValidateContext(null, null));
    if (newErrorResultValidationFailures.length !== 0) {
        throw new MsgPactError(
            `Failed internal msgPact validation: ${JSON.stringify(mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures))}`,
        );
    }
}
