package io.github.brenbar.uapi.internal;

import java.util.List;

import io.github.brenbar.uapi.RandomGenerator;

public class GenerateRandomValueOfType {
    static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator, UType thisType, boolean nullable,
            List<UTypeDeclaration> typeParameters) {
        if (nullable && !useBlueprintValue && randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters, generics, randomGenerator);
        }
    }
}
