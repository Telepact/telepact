package uapi.internal.validation;

import static uapi.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import uapi.internal.types.UStruct;

public class ValidateUnionStruct {
    static List<ValidationFailure> validateUnionStruct(
            UStruct unionStruct,
            String unionTag,
            Map<String, Object> actual, Map<String, Object> selectedTags, ValidateContext ctx) {
        final var selectedFields = selectedTags == null ? null : (List<String>) selectedTags.get(unionTag);
        return validateStructFields(unionStruct.fields, selectedFields, actual, ctx);
    }
}
