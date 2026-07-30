//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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

            final var validationFailures = new ArrayList<ValidationFailure>();
            for (var i = 0; i < l.size(); i += 1) {
                final var element = l.get(i);

                ctx.path.push("*");

                final var nestedValidationFailures = nestedTypeDeclaration.validate(element, ctx);

                ctx.path.pop();

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

            return validationFailures;
        } else {
            return getTypeUnexpectedValidationFailure(List.of(), value,
                    _ARRAY_NAME);
        }
    }
}
