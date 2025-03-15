package io.github.msgpact.internal.validation;

import static io.github.msgpact.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;

import java.util.List;

import io.github.msgpact.MsgPactError;
import io.github.msgpact.internal.types.VUnion;

public class ValidateResult {
    public static void validateResult(VUnion resultUnionType, Object errorResult) {
        final var newErrorResultValidationFailures = resultUnionType.validate(
                errorResult, List.of(), new ValidateContext(null, null));
        if (!newErrorResultValidationFailures.isEmpty()) {
            throw new MsgPactError(
                    "Failed internal msgPact validation: "
                            + mapValidationFailuresToInvalidFieldCases(newErrorResultValidationFailures));
        }
    }
}
