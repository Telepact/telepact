package uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MapValidationFailuresToInvalidFieldCases {

    public static List<Map<String, Object>> mapValidationFailuresToInvalidFieldCases(
            List<ValidationFailure> argumentValidationFailures) {
        final var validationFailureCases = new ArrayList<Map<String, Object>>();
        for (final var validationFailure : argumentValidationFailures) {
            final Map<String, Object> validationFailureCase = Map.of(
                    "path", validationFailure.path,
                    "reason", Map.of(validationFailure.reason, validationFailure.data));
            validationFailureCases.add(validationFailureCase);
        }

        return validationFailureCases;
    }
}
