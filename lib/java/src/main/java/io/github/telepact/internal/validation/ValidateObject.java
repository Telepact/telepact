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

import static io.github.telepact.internal.types.TObject._OBJECT_NAME;
import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TTypeDeclaration;

public class ValidateObject {

    public static List<ValidationFailure> validateObject(Object value, List<TTypeDeclaration> typeParameters,
            ValidateContext ctx) {
        if (value instanceof final Map<?, ?> m) {
            final var map = (Map<String, Object>) m;
            final var nestedTypeDeclaration = typeParameters.get(0);

            final var newValues = new HashMap<String, Object>();

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                
                ctx.path.push("*");
                
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, ctx);

                ctx.path.pop();

                if (ctx.newValue != null) {
                    newValues.put(k, ctx.newValue);
                    ctx.newValue = null;
                }

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = new ArrayList<>(f.path);
                    thisPath.add(0, k);

                    nestedValidationFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            for (var entry2 : newValues.entrySet()) {
                map.put(entry2.getKey(), entry2.getValue());
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _OBJECT_NAME);
        }
    }
}
