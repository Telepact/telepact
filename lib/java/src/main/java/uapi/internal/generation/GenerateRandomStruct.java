package uapi.internal.generation;

import static uapi.internal.generation.ConstructRandomStruct.constructRandomStruct;

import java.util.HashMap;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.types.UFieldDeclaration;

public class GenerateRandomStruct {
    public static Object generateRandomStruct(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields,
            RandomGenerator randomGenerator,
            Map<String, UFieldDeclaration> fields) {
        if (useBlueprintValue) {
            final var startingStructValue = (Map<String, Object>) blueprintValue;
            return constructRandomStruct(fields, startingStructValue, includeOptionalFields, randomizeOptionalFields,
                    randomGenerator);
        } else {
            return constructRandomStruct(fields, new HashMap<>(), includeOptionalFields, randomizeOptionalFields,
                    randomGenerator);
        }
    }
}
