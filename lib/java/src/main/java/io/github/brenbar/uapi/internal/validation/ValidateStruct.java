package io.github.brenbar.uapi.internal.validation;

import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.types.UStruct._STRUCT_NAME;
import static io.github.brenbar.uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.brenbar.uapi.internal.validation.ValidateStructFields.validateStructFields;

public class ValidateStruct {
    public static List<ValidationFailure> validateStruct(Object value, Map<String, Object> select, String fn,
            List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, String name, Map<String, UFieldDeclaration> fields) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = select == null ? null : (List<String>) select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, select, fn, typeParameters);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }
}
