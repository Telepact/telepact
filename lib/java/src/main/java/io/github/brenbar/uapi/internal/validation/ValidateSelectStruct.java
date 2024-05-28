package io.github.brenbar.uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UStruct;

import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

public class ValidateSelectStruct {
    static List<ValidationFailure> validateSelectStruct(UStruct structReference, List<Object> basePath,
            Object selectedFields) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        if (!(selectedFields instanceof List)) {
            return getTypeUnexpectedValidationFailure(basePath, selectedFields, "Array");
        }
        final List<Object> fields = (List<Object>) selectedFields;

        for (int i = 0; i < fields.size(); i += 1) {
            var field = fields.get(i);

            if (!(field instanceof String)) {
                final List<Object> thisPath = new ArrayList<>(basePath);
                thisPath.add(i);

                validationFailures.addAll(getTypeUnexpectedValidationFailure(thisPath, field, "String"));
                continue;
            }
            final String stringField = (String) field;

            if (!structReference.fields.containsKey(stringField)) {
                final List<Object> thisPath = new ArrayList<>(basePath);
                thisPath.add(i);

                validationFailures.add(new ValidationFailure(thisPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        return validationFailures;
    }
}
