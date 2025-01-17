package uapi.internal.validation;

import static uapi.internal.types.UUnion._UNION_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static uapi.internal.validation.ValidateUnionCases.validateUnionCases;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UStruct;

public class ValidateUnion {
    public static List<ValidationFailure> validateUnion(Object value,
            String name, Map<String, UStruct> cases, ValidateContext ctx) {
        if (value instanceof Map<?, ?> m) {
            Map<String, Object> selectedCases;
            if (name.startsWith("fn.")) {
                selectedCases = new HashMap<>();
                selectedCases.put(name, ctx.select == null ? null : ctx.select.get(name));
            } else {
                selectedCases = ctx.select == null ? null : (Map<String, Object>) ctx.select.get(name);
            }
            return validateUnionCases(cases, selectedCases, m, ctx);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _UNION_NAME);
        }
    }
}
