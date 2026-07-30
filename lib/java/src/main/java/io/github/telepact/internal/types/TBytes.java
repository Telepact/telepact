//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import static io.github.telepact.internal.generation.GenerateRandomBytes.generateRandomBytes;
import static io.github.telepact.internal.validation.ValidateBytes.validateBytes;


import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public class TBytes implements TType {

    public static final String _BYTES_NAME = "Bytes";

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public List<ValidationFailure> validate(Object value, List<TTypeDeclaration> typeParameters, ValidateContext ctx) {
        return validateBytes(value, ctx);
    }

    @Override
    public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        return generateRandomBytes(blueprintValue, useBlueprintValue, ctx);
    }

    @Override
    public String getName(ValidateContext ctx) {
        return _BYTES_NAME;
    }

}
