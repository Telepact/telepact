package io.github.brenbar.uapi.internal;

import java.util.List;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.types.UBoolean._BOOLEAN_NAME;

public class ValidateBoolean {
    public static List<ValidationFailure> validateBoolean(Object value) {
        if (value instanceof Boolean) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _BOOLEAN_NAME);
        }
    }
}
