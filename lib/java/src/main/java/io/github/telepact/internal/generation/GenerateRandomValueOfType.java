//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.generation;

import java.util.List;

import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;

public class GenerateRandomValueOfType {
    public static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue, TType thisType,
            boolean nullable,
            List<TTypeDeclaration> typeParameters, GenerateContext ctx) {
        if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
        }
    }
}
