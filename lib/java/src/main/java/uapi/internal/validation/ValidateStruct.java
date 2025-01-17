package uapi.internal.validation;

import static uapi.internal.types.UStruct._STRUCT_NAME;
import static uapi.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static uapi.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UTypeDeclaration;

public class ValidateStruct {
    public static List<ValidationFailure> validateStruct(Object value,
            String name, Map<String, UFieldDeclaration> fields, ValidateContext ctx) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = ctx.select == null ? null : (List<String>) ctx.select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, ctx);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }
}
