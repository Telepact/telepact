package io.github.brenbar.uapi.internal;

import java.util.List;

import io.github.brenbar.uapi.UApiError;

import static io.github.brenbar.uapi.internal.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

public class ValidateResult {
    static void validateResult(UUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, null, null, List.of(), List.of());
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new UApiError(
                    "Failed internal uAPI validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
