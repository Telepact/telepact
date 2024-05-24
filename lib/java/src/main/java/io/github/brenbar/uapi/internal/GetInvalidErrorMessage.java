package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.internal.types.UUnion;

import static io.github.brenbar.uapi.internal.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;
import static io.github.brenbar.uapi.internal.ValidateResult.validateResult;

public class GetInvalidErrorMessage {

    static Message getInvalidErrorMessage(String error, List<ValidationFailure> validationFailures,
            UUnion resultUnionType, Map<String, Object> responseHeaders) {
        final var validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
        final Map<String, Object> newErrorResult = Map.of(error,
                Map.of("cases", validationFailureCases));

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }
}
