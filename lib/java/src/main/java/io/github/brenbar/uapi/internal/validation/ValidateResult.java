package io.github.brenbar.uapi.internal.validation;

import static io.github.brenbar.uapi.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

import java.util.List;

import io.github.brenbar.uapi.UApiError;
import io.github.brenbar.uapi.internal.types.UUnion;

public class ValidateResult {
    public static void validateResult(UUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, null, null, List.of(), List.of());
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new UApiError(
                    "Failed internal uAPI validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
