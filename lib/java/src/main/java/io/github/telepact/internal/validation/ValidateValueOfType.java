package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.List;

import io.github.telepact.internal.types.VType;
import io.github.telepact.internal.types.VTypeDeclaration;

public class ValidateValueOfType {

    public static List<ValidationFailure> validateValueOfType(Object value,
            VType thisType, boolean nullable, List<VTypeDeclaration> typeParameters, ValidateContext ctx) {
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
