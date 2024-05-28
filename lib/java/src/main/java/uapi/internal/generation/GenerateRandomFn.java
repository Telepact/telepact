package uapi.internal.generation;

import static uapi.internal.generation.ConstructRandomUnion.constructRandomUnion;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.types.UStruct;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomFn {

    public static Object generateRandomFn(Object blueprintValue, boolean useBlueprintValue,
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
