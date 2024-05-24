package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.Prepend.prepend;
import static io.github.brenbar.uapi.internal.types.UArray._ARRAY_NAME;

public class ValidateArray {
    public static List<ValidationFailure> validateArray(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof final List l) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);
                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, select, fn, generics);
                final var index = i;

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> finalPath = prepend(index, f.path);
                    nestedValidationFailuresWithPath.add(new ValidationFailure(finalPath, f.reason,
                            f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value,
                    _ARRAY_NAME);
        }
    }
}
