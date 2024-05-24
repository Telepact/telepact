package io.github.brenbar.uapi.internal;

import java.util.List;

import static io.github.brenbar.uapi.internal._UBoolean._BOOLEAN_NAME;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

public class ValidateBoolean {
    static List<_ValidationFailure> validateBoolean(Object value) {
        if (value instanceof Boolean) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _BOOLEAN_NAME);
        }
    }
}
