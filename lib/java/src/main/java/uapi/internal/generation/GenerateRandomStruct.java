package uapi.internal.generation;

import static uapi.internal.generation.ConstructRandomStruct.constructRandomStruct;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UTypeDeclaration;

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
