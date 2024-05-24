package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static io.github.brenbar.uapi.internal.ValidateUnionCases.validateUnionCases;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.UUnion._UNION_NAME;

public class ValidateUnion {
    static List<ValidationFailure> validateUnion(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, String name, Map<String, UStruct> cases) {
        if (value instanceof Map<?, ?> m) {
            Map<String, Object> selectedCases;
            if (name.startsWith("fn.")) {
                selectedCases = new HashMap<>();
                selectedCases.put(name, select == null ? null : select.get(name));
            } else {
                selectedCases = select == null ? null : (Map<String, Object>) select.get(name);
            }
            return validateUnionCases(cases, selectedCases, m, select, fn, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _UNION_NAME);
        }
    }
}
