package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

public class ValidateValueOfType {

    static List<ValidationFailure> validateValueOfType(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> generics,
            UType thisType, boolean nullable, List<UTypeDeclaration> typeParameters) {
        if (value == null) {
            final boolean isNullable;
            if (thisType instanceof UGeneric g) {
                final int genericIndex = g.index;
                final var generic = generics.get(genericIndex);
                isNullable = generic.nullable;
            } else {
                isNullable = nullable;
            }

            if (!isNullable) {
                return getTypeUnexpectedValidationFailure(List.of(), value,
                        thisType.getName(generics));
            } else {
                return List.of();
            }
        } else {
            return thisType.validate(value, select, fn, typeParameters, generics);
        }
    }
}
