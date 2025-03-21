package io.github.telepact.internal.validation;

import static io.github.telepact.internal.types.VArray._ARRAY_NAME;
import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VTypeDeclaration;

public class ValidateArray {
    public static List<ValidationFailure> validateArray(Object value, List<VTypeDeclaration> typeParameters,
            ValidateContext ctx) {
        if (value instanceof final List l) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);
                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);
                final var index = i;

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> finalPath = new ArrayList<>(f.path);
                    finalPath.add(0, index);

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
