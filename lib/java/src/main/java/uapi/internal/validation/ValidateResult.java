package uapi.internal.validation;

import static uapi.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

import java.util.List;

import uapi.UApiError;
import uapi.internal.types.UUnion;

public class ValidateResult {
    public static void validateResult(UUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), new ValidateContext(null, null));
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new UApiError(
                    "Failed internal uAPI validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
