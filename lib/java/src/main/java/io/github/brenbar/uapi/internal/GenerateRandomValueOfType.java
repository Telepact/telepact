package io.github.brenbar.uapi.internal;

import java.util.List;

import io.github.brenbar.uapi._RandomGenerator;

public class GenerateRandomValueOfType {
    static Object generateRandomValueOfType(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator, _UType thisType, boolean nullable,
            List<_UTypeDeclaration> typeParameters) {
        if (nullable && !useBlueprintValue && randomGenerator.nextBoolean()) {
            return null;
        } else {
            return thisType.generateRandomValue(blueprintValue, useBlueprintValue, includeOptionalFields,
                    randomizeOptionalFields,
                    typeParameters, generics, randomGenerator);
        }
    }
}
