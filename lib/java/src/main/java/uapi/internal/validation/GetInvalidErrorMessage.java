package uapi.internal.validation;

import static uapi.internal.validation.MapValidationFailuresToInvalidFieldCases.mapValidationFailuresToInvalidFieldCases;
import static uapi.internal.validation.ValidateResult.validateResult;

import java.util.List;
import java.util.Map;

import uapi.Message;
import uapi.internal.types.UUnion;

public class GetInvalidErrorMessage {

    public static Message getInvalidErrorMessage(String error, List<ValidationFailure> validationFailures,
            UUnion resultUnionType, Map<String, Object> responseHeaders) {
        final var validationFailureCases = mapValidationFailuresToInvalidFieldCases(validationFailures);
        final Map<String, Object> newErrorResult = Map.of(error,
                Map.of("cases", validationFailureCases));

        validateResult(resultUnionType, newErrorResult);
        return new Message(responseHeaders, newErrorResult);
    }
}
