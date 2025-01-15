package uapi.internal.generation;

import java.util.List;

import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomValueOfType {
    public static Object generateRandomValueOfType(UType thisType, boolean nullable,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        if (nullable && !ctx.useBlueprintValue && ctx.randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(ctx.copyWithNewTypeParameters(typeParameters));
        }
    }
}
