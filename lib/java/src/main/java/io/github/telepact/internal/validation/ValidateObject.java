//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                final var k = (String) entry.getKey();
                final var v = entry.getValue();
                
                ctx.path.push("*");
                
                final var nestedValidationFailures = nestedTypeDeclaration.validate(v, ctx);

                ctx.path.pop();

                final var nestedValidationFailuresWithPath = new ArrayList<ValidationFailure>();
                for (var f : nestedValidationFailures) {
                    final List<Object> thisPath = new ArrayList<>(f.path);
                    thisPath.add(0, k);

                    nestedValidationFailuresWithPath.add(new ValidationFailure(thisPath, f.reason, f.data));
                }

                validationFailures.addAll(nestedValidationFailuresWithPath);
            }

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value, _OBJECT_NAME);
        }
    }
}
