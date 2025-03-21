package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

import java.util.List;

import io.github.telepact.TelepactError;
import io.github.telepact.internal.types.VUnion;

public class ValidateResult {
    public static void validateResult(VUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), new ValidateContext(null, null));
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new TelepactError(
                    "Failed internal telepact validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
