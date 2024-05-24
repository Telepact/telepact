package io.github.brenbar.uapi.internal.validation;

import java.util.List;

import static io.github.brenbar.uapi.internal.types.UString._STRING_NAME;
import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

public class ValidateString {
    public static List<ValidationFailure> validateString(Object value) {
        if (value instanceof String) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRING_NAME);
        }
    }
}
