package uapi.internal.generation;

import java.util.Map;
import java.util.TreeMap;

public class GenerateRandomObject {
    public static Object generateRandomObject(GenerateContext ctx) {
        final var nestedTypeDeclaration = ctx.typeParameters.get(0);

        if (ctx.useBlueprintValue) {
            final var startingObj = (Map<String, Object>) ctx.blueprintValue;

            final var obj = new TreeMap<String, Object>();
            for (final var startingObjEntry : startingObj.entrySet()) {
                final var key = startingObjEntry.getKey();
                final var startingObjValue = startingObjEntry.getValue();
                final var value = nestedTypeDeclaration
                        .generateRandomValue(ctx.copyWithNewBlueprintValue(startingObjValue));
                obj.put(key, value);
            }

            return obj;
        } else {
            final var length = ctx.randomGenerator.nextCollectionLength();

            final var obj = new TreeMap<String, Object>();
            for (int i = 0; i < length; i += 1) {
                final var key = ctx.randomGenerator.nextString();
                final var value = nestedTypeDeclaration.generateRandomValue(ctx);
                obj.put(key, value);
            }

            return obj;
        }
    }
}
