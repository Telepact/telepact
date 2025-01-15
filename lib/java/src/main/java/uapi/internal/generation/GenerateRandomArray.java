package uapi.internal.generation;

import java.util.ArrayList;
import java.util.List;

public class GenerateRandomArray {
    public static Object generateRandomArray(GenerateContext ctx) {
        final var nestedTypeDeclaration = ctx.typeParameters.get(0);

        if (ctx.useBlueprintValue) {
            final var startingArray = (List<Object>) ctx.blueprintValue;

            final var array = new ArrayList<Object>();
            for (final var startingArrayValue : startingArray) {
                final var value = nestedTypeDeclaration
                        .generateRandomValue(ctx.copyWithNewBlueprintValue(startingArrayValue));

                array.add(value);
            }

            return array;
        } else {
            final var length = ctx.randomGenerator.nextCollectionLength();

            final var array = new ArrayList<Object>();
            for (int i = 0; i < length; i += 1) {
                final var value = nestedTypeDeclaration.generateRandomValue(ctx);

                array.add(value);
            }

            return array;
        }
    }
}
