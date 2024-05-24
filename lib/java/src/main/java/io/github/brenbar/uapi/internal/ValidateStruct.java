package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal._UStruct._STRUCT_NAME;
import static io.github.brenbar.uapi.internal.ValidateStructFields.validateStructFields;

public class ValidateStruct {
    static List<_ValidationFailure> validateStruct(Object value, Map<String, Object> select, String fn,
            List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, String name, Map<String, _UFieldDeclaration> fields) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = select == null ? null : (List<String>) select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, select, fn, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }
}
