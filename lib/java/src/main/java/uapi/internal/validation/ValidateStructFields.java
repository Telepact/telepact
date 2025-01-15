package uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UTypeDeclaration;

public class ValidateStructFields {
    static List<ValidationFailure> validateStructFields(
            Map<String, UFieldDeclaration> fields,
            List<String> selectedFields,
            Map<String, Object> actualStruct, Map<String, Object> select, String fn) {
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

            final UTypeDeclaration refFieldTypeDeclaration = referenceField.typeDeclaration;

            final var nestedValidationFailures = refFieldTypeDeclaration.validate(fieldValue, select, fn);

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
