//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomSelect.generateRandomSelect;
import static io.github.telepact.internal.validation.ValidateSelect.validateSelect;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TSelect implements TType {

    public static final String _SELECT = "Object";

    public final Map<String, Object> possibleSelects = new HashMap<>();

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj,
            List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateSelect(givenObj, this.possibleSelects, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomSelect(this.possibleSelects, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _SELECT;
    }

}
