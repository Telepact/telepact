//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
