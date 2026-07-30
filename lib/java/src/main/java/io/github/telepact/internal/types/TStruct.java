//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomStruct.generateRandomStruct;
import static io.github.telepact.internal.validation.ValidateStruct.validateStruct;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TStruct implements TType {

    public static final String _STRUCT_NAME = "Object";

    public final String name;
    public final Map<String, TFieldDeclaration> fields;

    public TStruct(String name, Map<String, TFieldDeclaration> fields) {
        this.name = name;
        this.fields = fields;
    }

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateStruct(value, this.name, this.fields, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomStruct(blueprintValue, useBlueprintValue, this.fields, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _STRUCT_NAME;
    }
}
