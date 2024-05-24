package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;

import static io.github.brenbar.uapi.internal.ConstructRandomUnion.constructRandomUnion;

public class GenerateRandomFn {

    static Object generateRandomFn(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            List<UTypeDeclaration> generics, RandomGenerator randomGenerator, Map<String, UStruct> callCases) {
        if (useBlueprintValue) {
            final var startingFnValue = (Map<String, Object>) blueprintValue;
            return constructRandomUnion(callCases, startingFnValue, includeOptionalFields, randomizeOptionalFields,
                    List.of(), randomGenerator);
        } else {
            return constructRandomUnion(callCases, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    List.of(), randomGenerator);
        }
    }
}
