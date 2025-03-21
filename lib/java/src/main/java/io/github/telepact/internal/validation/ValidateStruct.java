//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

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
