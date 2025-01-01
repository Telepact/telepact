package uapi.internal.validation;

import static uapi.internal.types.UUnion._UNION_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static uapi.internal.validation.ValidateUnionCases.validateUnionCases;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UStruct;

public class ValidateUnion {
    public static List<ValidationFailure> validateUnion(Object value, Map<String, Object> select, String fn,
            String name, Map<String, UStruct> cases) {
        if (value instanceof Map<?, ?> m) {
            Map<String, Object> selectedCases;
            if (name.startsWith("fn.")) {
                selectedCases = new HashMap<>();
                selectedCases.put(name, select == null ? null : select.get(name));
            } else {
                selectedCases = select == null ? null : (Map<String, Object>) select.get(name);
            }
            return validateUnionCases(cases, selectedCases, m, select, fn);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _UNION_NAME);
        }
    }
}
