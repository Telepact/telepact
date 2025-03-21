package io.github.telepact.internal.validation;

import static io.github.telepact.internal.types.VStruct._STRUCT_NAME;
import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.telepact.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VTypeDeclaration;

public class ValidateStruct {
    public static List<ValidationFailure> validateStruct(Object value,
            String name, Map<String, VFieldDeclaration> fields, ValidateContext ctx) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = ctx.select == null ? null : (List<String>) ctx.select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, ctx);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }
}
