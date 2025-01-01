package uapi.internal.validation;

import static uapi.internal.types.UStruct._STRUCT_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static uapi.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UTypeDeclaration;

public class ValidateStruct {
    public static List<ValidationFailure> validateStruct(Object value, Map<String, Object> select, String fn,
            String name, Map<String, UFieldDeclaration> fields) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = select == null ? null : (List<String>) select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, select, fn);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }
}
