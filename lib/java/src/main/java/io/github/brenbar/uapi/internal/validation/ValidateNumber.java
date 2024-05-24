package io.github.brenbar.uapi.internal.validation;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;
import java.util.Map;

import static io.github.brenbar.uapi.internal.types.UNumber._NUMBER_NAME;
import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

public class ValidateNumber {
    public static List<ValidationFailure> validateNumber(Object value) {
        if (value instanceof BigInteger bi || value instanceof BigDecimal bd) {
            return List.of(
                    new ValidationFailure(List.of(), "NumberOutOfRange", Map.of()));
        } else if (value instanceof Number) {
            return List.of();
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _NUMBER_NAME);
        }
    }
}
