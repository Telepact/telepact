package io.github.brenbar.uapi.internal.validation;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UStruct;

import static io.github.brenbar.uapi.internal.Append.append;
import static io.github.brenbar.uapi.internal.AsList.asList;
import static io.github.brenbar.uapi.internal.AsString.asString;
import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

public class ValidateSelectStruct {
    static List<ValidationFailure> validateSelectStruct(UStruct structReference, List<Object> basePath,
            Object selectedFields) {
        final var validationFailures = new ArrayList<ValidationFailure>();

        final List<Object> fields;
        try {
            fields = asList(selectedFields);
        } catch (ClassCastException e) {
            return getTypeUnexpectedValidationFailure(basePath, selectedFields, "Array");
        }

        for (int i = 0; i < fields.size(); i += 1) {
            var field = fields.get(i);
            String stringField;
            try {
                stringField = asString(field);
            } catch (ClassCastException e) {
                final List<Object> thisPath = append(basePath, i);

                validationFailures.addAll(getTypeUnexpectedValidationFailure(thisPath, field, "String"));
                continue;
            }
            if (!structReference.fields.containsKey(stringField)) {
                final List<Object> thisPath = append(basePath, i);

                validationFailures.add(new ValidationFailure(thisPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        return validationFailures;
    }
}
