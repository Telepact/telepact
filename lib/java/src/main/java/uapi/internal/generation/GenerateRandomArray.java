package uapi.internal.generation;

import java.util.ArrayList;
import java.util.List;

import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomArray {
    public static Object generateRandomArray(Object blueprintValue, boolean useBlueprintValue,
            List<UTypeDeclaration> typeParameters, GenerateContext ctx) {
        final var nestedTypeDeclaration = typeParameters.get(0);

        if (useBlueprintValue) {
            final var startingArray = (List<Object>) blueprintValue;

            final var array = new ArrayList<Object>();
            for (final var startingArrayValue : startingArray) {
                final var value = nestedTypeDeclaration
                        .generateRandomValue(startingArrayValue, true, ctx);

                array.add(value);
            }

            return array;
        } else {
            final var length = ctx.randomGenerator.nextCollectionLength();

            final var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                final var value = nestedTypeDeclaration.generateRandomValue(null, false, ctx);

                array.add(value);
            }

            return array;
        }
    }
}
