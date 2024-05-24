package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import static io.github.brenbar.uapi.internal.Prepend.prepend;

public class ValidateHeaders {
    static List<_ValidationFailure> validateHeaders(
            Map<String, Object> headers, Map<String, _UFieldDeclaration> parsedRequestHeaders, _UFn functionType) {
        final var validationFailures = new ArrayList<_ValidationFailure>();

        for (final var entry : headers.entrySet()) {
            final var header = entry.getKey();
            final var headerValue = entry.getValue();
            final var field = parsedRequestHeaders.get(header);
            if (field != null) {
                final var thisValidationFailures = field.typeDeclaration.validate(headerValue, null, functionType.name,
                        List.of());
                final var thisValidationFailuresPath = thisValidationFailures.stream()
                        .map(e -> new _ValidationFailure(prepend(header, e.path), e.reason, e.data)).toList();
                validationFailures.addAll(thisValidationFailuresPath);
            }
        }

        return validationFailures;
    }
}
