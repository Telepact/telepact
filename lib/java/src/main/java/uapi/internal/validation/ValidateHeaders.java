package uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UFn;

public class ValidateHeaders {
    public static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, Map<String, UFieldDeclaration> parsedRequestHeaders, UFn functionType) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        for (final var entry : headers.entrySet()) {
            final var header = entry.getKey();
            final var headerValue = entry.getValue();
            final var field = parsedRequestHeaders.get(header);
            if (field != null) {
                final var thisValidationFailures = field.typeDeclaration.validate(headerValue, null, functionType.name);
                final var thisValidationFailuresPath = thisValidationFailures.stream()
                        .map(e -> {
                            final var path = new ArrayList<>(e.path);
                            path.add(0, header);

                            return new ValidationFailure(path, e.reason, e.data);
                        }).toList();
                validationFailures.addAll(thisValidationFailuresPath);
            }
        }

        return validationFailures;
    }
}
