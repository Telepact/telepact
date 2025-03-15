package io.github.msgpact.internal.validation;

import static io.github.msgpact.internal.types.VString._STRING_NAME;
import static io.github.msgpact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.List;

public class ValidateString {
    public static List<ValidationFailure> validateString(Object value) {
        if (value instanceof String) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRING_NAME);
        }
    }
}
