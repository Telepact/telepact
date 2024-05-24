package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.Prepend.prepend;
import static io.github.brenbar.uapi.internal.types.UObject._OBJECT_NAME;

public class ValidateObject {

    public static List<ValidationFailure> validateObject(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics) {
        if (value instanceof final Map<?, ?> m) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, select, fn, generics);

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = prepend(k, f.path);

                    nestedValidationFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _OBJECT_NAME);
        }
    }
}
