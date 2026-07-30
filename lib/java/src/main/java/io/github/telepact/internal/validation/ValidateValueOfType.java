//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.validation;

import static io.github.telepact.internal.validation.GetTypeUnexpectedValidationFailure.getTypeUnexpectedValidationFailure;

import java.util.List;

import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;

public class ValidateValueOfType {

    public static List<ValidationFailure> validateValueOfType(Object value,
            TType thisType, boolean nullable, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        if (value == null) {

            if (!nullable) {
                return getTypeUnexpectedValidationFailure(List.of(), value,
                        thisType.getName(ctx));
            } else {
                return List.of();
            }
        } else {
            return thisType.validate(value, typeParameters, ctx);
        }
    }
}
