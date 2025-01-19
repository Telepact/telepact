package uapi.internal.validation;

import static uapi.internal.types.UUnion._UNION_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static uapi.internal.validation.ValidateUnionTags.validateUnionTags;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UStruct;

public class ValidateUnion {
    public static List<ValidationFailure> validateUnion(Object value,
            String name, Map<String, UStruct> tags, ValidateContext ctx) {
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
