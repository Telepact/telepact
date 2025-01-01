package uapi.internal.generation;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import uapi.RandomGenerator;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomObject {
    public static Object generateRandomObject(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useBlueprintValue) {
            final var startingObj = (Map<String, Object>) blueprintValue;

            final var obj = new TreeMap<String, Object>();
            for (final var startingObjEntry : startingObj.entrySet()) {
                final var key = startingObjEntry.getKey();
                final var startingObjValue = startingObjEntry.getValue();
                final var value = nestedTypeDeclaration.generateRandomValue(startingObjValue, true,
                        includeOptionalFields, randomizeOptionalFields, randomGenerator);
                obj.put(key, value);
            }

            return obj;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                final var key = randomGenerator.nextString();
                final var value = nestedTypeDeclaration.generateRandomValue(null, false, includeOptionalFields,
                        randomizeOptionalFields,
                        randomGenerator);
                obj.put(key, value);
            }

            return obj;
        }
    }
}
