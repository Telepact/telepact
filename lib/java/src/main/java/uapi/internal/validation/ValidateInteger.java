package uapi.internal.validation;

import static uapi.internal.types.UInteger._INTEGER_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ValidateInteger {
    public static List<ValidationFailure> validateInteger(Object value) {
        if (value instanceof Long || value instanceof Integer) {
            return List.of();
        } else if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return List.of(
                    new ValidationFailure(new ArrayList<Object>(), "NumberOutOfRange", Map.of()));
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _INTEGER_NAME);
        }
    }
}
