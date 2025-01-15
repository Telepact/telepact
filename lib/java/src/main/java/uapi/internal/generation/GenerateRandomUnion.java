package uapi.internal.generation;

import static uapi.internal.generation.GenerateRandomStruct.generateRandomStruct;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Map;

import uapi.internal.types.UStruct;

public class GenerateRandomUnion {
    public static Object generateRandomUnion(Map<String, UStruct> unionCasesReference, GenerateContext ctx) {
        if (ctx.useBlueprintValue) {
            final var startingUnion = (Map<String, Object>) ctx.blueprintValue;
            final var entry = startingUnion.entrySet().stream().findAny().get();
            final var unionCase = entry.getKey();
            final var unionStructType = unionCasesReference.get(unionCase);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase,
                    generateRandomStruct(unionStructType.fields, ctx.copyWithNewBlueprintValue(unionStartingStruct)));
        } else {
            final var sortedUnionCasesReference = new ArrayList<>(unionCasesReference.entrySet());

            Collections.sort(sortedUnionCasesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            final var randomIndex = ctx.randomGenerator.nextIntWithCeiling(sortedUnionCasesReference.size() - 1);
            final var unionEntry = sortedUnionCasesReference.get(randomIndex);
            final var unionCase = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionCase,
                    generateRandomStruct(unionData.fields, ctx));
        }
    }
}
