package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi._RandomGenerator;

import static io.github.brenbar.uapi.internal.ConstructRandomUnion.constructRandomUnion;

public class GenerateRandomFn {

    static Object generateRandomFn(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, _RandomGenerator randomGenerator, Map<String, _UStruct> callCases) {
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
