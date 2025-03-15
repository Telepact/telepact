package io.github.msgpact.internal.validation;

import static io.github.msgpact.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import io.github.msgpact.internal.types.VStruct;

public class ValidateUnionStruct {
    static List<ValidationFailure> validateUnionStruct(
            VStruct unionStruct,
            String unionTag,
            Map<String, Object> actual, Map<String, Object> selectedTags, ValidateContext ctx) {
        final var selectedFields = selectedTags == null ? null : (List<String>) selectedTags.get(unionTag);
        return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
    }
}
