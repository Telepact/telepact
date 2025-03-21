package io.github.telepact.internal.validation;

import static io.github.telepact.internal.types.VUnion._UNION_NAME;
import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.telepact.internal.validation.ValidateUnionTags.validateUnionTags;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VStruct;

public class ValidateUnion {
    public static List<ValidationFailure> validateUnion(Object value,
            String name, Map<String, VStruct> tags, ValidateContext ctx) {
        if (value instanceof Map<?, ?> m) {
            Map<String, Object> selectedTags;
            if (name.startsWith("fn.")) {
                selectedTags = new HashMap<>();
                selectedTags.put(name, ctx.select == null ? null : ctx.select.get(name));
            } else {
                selectedTags = ctx.select == null ? null : (Map<String, Object>) ctx.select.get(name);
            }
            return validateUnionTags(tags, selectedTags, m, ctx);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _UNION_NAME);
        }
    }
}
