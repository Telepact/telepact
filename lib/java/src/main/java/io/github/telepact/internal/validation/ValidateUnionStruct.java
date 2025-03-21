package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VStruct;

public class ValidateUnionStruct {
    static List<ValidationFailure> validateUnionStruct(
            VStruct unionStruct,
            String unionTag,
            Map<String, Object> actual, Map<String, Object> selectedTags, ValidateContext ctx) {
        final var selectedFields = selectedTags == null ? null : (List<String>) selectedTags.get(unionTag);
        return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
    }
}
