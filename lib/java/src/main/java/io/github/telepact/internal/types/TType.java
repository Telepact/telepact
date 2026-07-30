//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.types;

import java.util.List;

import io.github.telepact.internal.generation.GenerateContext;
import io.github.telepact.internal.validation.ValidateContext;
import io.github.telepact.internal.validation.ValidationFailure;

public interface TType {
        public int getTypeParameterCount();

        public List<ValidationFailure> validate(Object value,
                        List<TTypeDeclaration> typeParameters, ValidateContext ctx);

        public Object generateRandomValue(Object blueprintValue, boolean useBlueprintValue,
                        List<TTypeDeclaration> typeParameters, GenerateContext ctx);

        public String getName(ValidateContext ctx);
}
