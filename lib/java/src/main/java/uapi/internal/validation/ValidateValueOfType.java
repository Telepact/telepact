package uapi.internal.validation;

import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.List;

import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;

public class ValidateValueOfType {

    public static List<ValidationFailure> validateValueOfType(Object value,
            UType thisType, boolean nullable, List<UTypeDeclaration> typeParameters, ValidateContext ctx) {
        if (value == null) {

            if (!nullable) {
                return getTypeUnexpectedValidationFailure(List.of(), value,
                        thisType.getName());
            } else {
                return List.of();
            }
        } else {
            return thisType.validate(value, typeParameters, ctx);
        }
    }
}
