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
import io.github.telepact.internal.types.TTypeDeclaration;

public class ValidateStructFields {
    static List<ValidationFailure> validateStructFields(
            Map<String, TFieldDeclaration> fields,
            List<String> selectedFields,
            Map<String, Object> actualStruct, ValidateContext ctx) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        final var missingFields = new ArrayList<String>();
        for (final var entry : fields.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldDeclaration = entry.getValue();
            final boolean isOptional = fieldDeclaration.optional;
            final boolean isOmittedBySelect = selectedFields != null && !selectedFields.contains(fieldName);
            if (!actualStruct.containsKey(fieldName) && !isOptional && !isOmittedBySelect) {
                missingFields.add(fieldName);
            }
        }

        for (final var missingField : missingFields) {
            final var validationFailure = new ValidationFailure(List.of(),
                    "RequiredObjectKeyMissing",
                    Map.of("key", missingField));

            validationFailures.add(validationFailure);
        }

        for (final var entry : actualStruct.entrySet()) {
            final var fieldName = entry.getKey();
            final var fieldValue = entry.getValue();

            final var referenceField = fields.get(fieldName);
            if (referenceField == null) {
                var validationFailure = new ValidationFailure(List.of(fieldName), "ObjectKeyDisallowed",
                        Map.of());

                validationFailures.add(validationFailure);
                continue;
            }

            final TTypeDeclaration refFieldTypeDeclaration = referenceField.typeDeclaration;

            final var nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, ctx);

            final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
            for (final var f : nestedValidationFailures) {
                final List<Object> thisPath = new ArrayList<>(f.path);
                thisPath.add(0, fieldName);

                nestedValidationFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
            }

            validationFailures.addAll(nestedValidationFailuresWithPath);
        }

        return validationFailures;
    }
}
