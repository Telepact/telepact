package uapi.internal.generation;

import static uapi.internal.generation.ConstructRandomUnion.constructRandomUnion;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.types.UStruct;
import uapi.internal.types.UTypeDeclaration;

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
