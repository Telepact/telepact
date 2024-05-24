package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;

import io.github.brenbar.uapi._RandomGenerator;

public class GenerateRandomArray {
    static Object generateRandomArray(Object blueprintValue, boolean useBlueprintValue,
            boolean includeOptionalFields, boolean randomizeOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics,
            _RandomGenerator randomGenerator) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useBlueprintValue) {
            final var startingArray = (List<Object>) blueprintValue;

            final var array = new ArrayList<Object>();
            for (final var startingArrayValue : startingArray) {
                final var value = nestedTypeDeclaration.generateRandomValue(startingArrayValue, true,
                        includeOptionalFields, randomizeOptionalFields, generics, randomGenerator);

                array.add(value);
            }

            return array;
        } else {
            final var length = randomGenerator.nextCollectionLength();

            final var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                final var value = nestedTypeDeclaration.generateRandomValue(null, false,
                        includeOptionalFields, randomizeOptionalFields,
                        generics, randomGenerator);

                array.add(value);
            }

            return array;
        }
    }
}
