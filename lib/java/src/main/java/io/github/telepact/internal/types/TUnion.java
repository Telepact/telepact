//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomUnion.generateRandomUnion;
import static io.github.telepact.internal.validation.ValidateUnion.validateUnion;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TUnion implements TType {

    public static final String _UNION_NAME = "Object";

    public final String name;
    public final Map<String, TStruct> tags;
    public final Map<String, Integer> tagIndices;

    public TUnion(String name, Map<String, TStruct> tags, Map<String, Integer> tagIndices) {
        this.name = name;
        this.tags = tags;
        this.tagIndices = tagIndices;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateUnion(value, this.name, this.tags, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomUnion(blueprintValue, useBlueprintValue, this.tags, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _UNION_NAME;
    }
}
