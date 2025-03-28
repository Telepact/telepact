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

import static io.github.telepact.internal.types.TArray._ARRAY_NAME;
import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

import io.github.telepact.internal.types.TTypeDeclaration;

public class ValidateArray {
    public static List<ValidationFailure> validateArray(Object value, List<TTypeDeclaration> typeParameters,
            ValidateContext ctx) {
        if (value instanceof final List l) {
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var newValues = new HashMap<Integer, Object>();

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);

                ctx.path.push("*");

                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);

                ctx.path.pop();

                if (ctx.newValue != null) {
                    newValues.put(i, ctx.newValue);
                    ctx.newValue = null;
                }
                
                final var index = i;

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> finalPath = new ArrayList<>(f.path);
                    finalPath.add(0, index);

                    nestedValidationFailuresWithPath.add(new ValidationFailure(finalPath, f.reason,
                            f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            for (var entry : newValues.entrySet()) {
                l.set(entry.getKey(), entry.getValue());
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value,
                    _ARRAY_NAME);
        }
    }
}
