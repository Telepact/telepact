package io.github.telepact.internal.generation;

import java.util.List;

import io.github.telepact.internal.types.VType;
import io.github.telepact.internal.types.VTypeDeclaration;

public class GenerateRandomValueOfType {
    public static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue, VType thisType,
            boolean nullable,
            List<VTypeDeclaration> typeParameters, GenerateContext ctx) {
        if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
        }
    }
}
