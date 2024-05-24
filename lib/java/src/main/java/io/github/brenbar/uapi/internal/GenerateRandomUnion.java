package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.ConstructRandomUnion.constructRandomUnion;

public class GenerateRandomUnion {
    public static Object generateRandomUnion(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics,
            RandomGenerator randomGenerator, Map<String, UStruct> cases) {
        if (useBlueprintValue) {
            final var startingUnionCase = (Map<String, Object>) blueprintValue;
            return constructRandomUnion(cases, startingUnionCase, includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        } else {
            return constructRandomUnion(cases, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    typeParameters, randomGenerator);
        }
    }
}
