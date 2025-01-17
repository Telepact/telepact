package uapi.internal.validation;

import static uapi.internal.types.UObject._OBJECT_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UTypeDeclaration;

public class ValidateObject {

    public static List<ValidationFailure> validateObject(Object value, List<UTypeDeclaration> typeParameters,
            ValidateContext ctx) {
        if (value instanceof final Map<?, ?> m) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<?, ?> entry : m.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, ctx);

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = new ArrayList<>(f.path);
                    thisPath.add(0, k);

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
