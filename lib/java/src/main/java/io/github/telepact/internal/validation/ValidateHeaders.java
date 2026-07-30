//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TFieldDeclaration;

public class ValidateHeaders {
    public static List<ValidationFailure> validateHeaders(
            Map<String, Object> headers, Map<String, TFieldDeclaration> parsedRequestHeaders, String functionName) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        for (final var entry : headers.entrySet()) {
            final var header = entry.getKey();
            final var headerValue = entry.getValue();

            if (!header.startsWith("@")) {
                validationFailures.add(new ValidationFailure(List.of(header), "RequiredObjectKeyPrefixMissing", Map.of("prefix", "@")));
            }

            final var field = parsedRequestHeaders.get(header);
            if (field != null) {
                final var thisValidationFailures = field.typeDeclaration.validate(headerValue,
                        new ValidateContext(null, functionName,  false));
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
