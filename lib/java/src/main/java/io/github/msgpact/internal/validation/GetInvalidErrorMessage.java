package io.github.msgpact.internal.validation;

import static io.github.msgpact.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;
import static io.github.msgpact.internal.validation.ValidateResult.validateResult;

import java.util.List;
import java.util.Map;

import io.github.msgpact.Message;
import io.github.msgpact.internal.types.VUnion;

public class GetInvalidErrorMessage {

    public static Message getInvalidErrorMessage(String error, List<ValidationFailure> validationFailures,
            VUnion resultUnionType, Map<String, Object> responseHeaders) {
        final var validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
        final Map<String, Object> newErrorResult = Map.of(error,
                Map.of("cases", validationFailureCases));

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }
}
