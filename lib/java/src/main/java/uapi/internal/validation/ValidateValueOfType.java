package uapi.internal.validation;

import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.List;
import java.util.Map;

import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;

public class ValidateValueOfType {

    public static List<ValidationFailure> validateValueOfType(Object value, Map<String, Object> select, String fn,
            UType thisType, boolean nullable, List<UTypeDeclaration> typeParameters) {
        if (value == null) {

            if (!nullable) {
                return getTypeUnexpectedValidationFailure(List.of(), value,
                        thisType.getName());
            } else {
                return List.of();
            }
        } else {
            return thisType.validate(value, select, fn, typeParameters);
        }
    }
}
