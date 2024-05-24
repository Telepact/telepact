package io.github.brenbar.uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UFn;

import static io.github.brenbar.uapi.internal.Prepend.prepend;

public class ValidateHeaders {
    public static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, Map<String, UFieldDeclaration> parsedRequestHeaders, UFn functionType) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        for (final var entry : headers.entrySet()) {
            final var header = entry.getKey();
            final var headerValue = entry.getValue();
            final var field = parsedRequestHeaders.get(header);
            if (field != null) {
                final var thisValidationFailures = field.typeDeclaration.validate(headerValue, null, functionType.name,
                        List.of());
                final var thisValidationFailuresPath = thisValidationFailures.stream()
                        .map(e -> new ValidationFailure(prepend(header, e.path), e.reason, e.data)).toList();
                validationFailures.addAll(thisValidationFailuresPath);
            }
        }

        return validationFailures;
    }
}
