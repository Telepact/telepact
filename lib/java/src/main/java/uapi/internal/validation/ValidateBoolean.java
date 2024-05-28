package uapi.internal.validation;

import static uapi.internal.types.UBoolean._BOOLEAN_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.List;

public class ValidateBoolean {
    public static List<ValidationFailure> validateBoolean(Object value) {
        if (value instanceof Boolean) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _BOOLEAN_NAME);
        }
    }
}
