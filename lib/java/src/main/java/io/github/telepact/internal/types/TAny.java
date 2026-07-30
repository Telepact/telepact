//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomAny.generateRandomAny;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TAny implements TType {

    static final String _ANY_NAME = "Any";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(
            Object value, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return List.of();
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomAny(ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _ANY_NAME;
    }
}
