//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomBoolean.generateRandomBoolean;
import static io.github.telepact.internal.validation.ValidateBoolean.validateBoolean;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TBoolean implements TType {

    public static final String _BOOLEAN_NAME = "Boolean";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateBoolean(value);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomBoolean(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _BOOLEAN_NAME;
    }

}
