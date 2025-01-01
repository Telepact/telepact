package uapi.internal.generation;

import java.util.List;

import uapi.RandomGenerator;
import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomValueOfType {
    public static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields,
            RandomGenerator randomGenerator, UType thisType, boolean nullable,
            List<UTypeDeclaration> typeParameters) {
        if (nullable && !useBlueprintValue && randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters, randomGenerator);
        }
    }
}
