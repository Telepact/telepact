package uapi.internal.generation;

import java.util.List;

import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomValueOfType {
    public static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue, UType thisType,
            boolean nullable,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        if (nullable && !useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, typeParameters, ctx);
        }
    }
}
