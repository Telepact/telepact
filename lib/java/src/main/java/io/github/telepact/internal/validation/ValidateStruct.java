//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.validation;

import static io.github.telepact.internal.types.TStruct._STRUCT_NAME;
import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;
import static io.github.telepact.internal.validation.ValidateStructFields.validateStructFields;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TTypeDeclaration;

public class ValidateStruct {
    public static List<ValidationFailure> validateStruct(Object value,
            String name, Map<String, TFieldDeclaration> fields, ValidateContext ctx) {
        if (value instanceof Map<?, ?> m) {
            final var selectedFields = ctx.select == null ? null : (List<String>) ctx.select.get(name);
            return validateStructFields(fields, selectedFields, (Map<String, Object>) m, ctx);
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _STRUCT_NAME);
        }
    }
}
