package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi._RandomGenerator;

import static io.github.brenbar.uapi.internal.ConstructRandomUnion.constructRandomUnion;

public class GenerateRandomUnion {
    static Object generateRandomUnion(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator, Map<String, _UStruct> cases) {
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
