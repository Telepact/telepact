package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.ConstructRandomStruct.constructRandomStruct;

public class GenerateRandomStruct {
    public static Object generateRandomStruct(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, RandomGenerator randomGenerator,
            Map<String, UFieldDeclaration> fields) {
        if (useBlueprintValue) {
            final var startingStructValue = (Map<String, Object>) blueprintValue;
            return constructRandomStruct(fields, startingStructValue, includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        } else {
            return constructRandomStruct(fields, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        }
    }
}
