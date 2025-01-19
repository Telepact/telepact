package uapi.internal.generation;

import static uapi.internal.generation.GenerateRandomStruct.generateRandomStruct;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UStruct;
import uapi.internal.types.UTypeDeclaration;

public class GenerateRandomUnion {
    public static Object generateRandomUnion(Object blueprintValue,
            boolean useBlueprintValue, Map<String, UStruct> unionTagsReference,
            GenerateContext ctx) {
        if (useBlueprintValue) {
            final var startingUnion = (Map<String, Object>) blueprintValue;
            final var entry = startingUnion.entrySet().stream().findAny().get();
            final var unionTag = entry.getKey();
            final var unionStructType = unionTagsReference.get(unionTag);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionTag);

            return Map.of(unionTag,
                    generateRandomStruct(unionStartingStruct, true, unionStructType.fields, ctx));
        } else {
            final var sortedUnionTagsReference = new ArrayList<>(unionTagsReference.entrySet());

            Collections.sort(sortedUnionTagsReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            final var randomIndex = ctx.randomGenerator.nextIntWithCeiling(sortedUnionTagsReference.size() - 1);
            final var unionEntry = sortedUnionTagsReference.get(randomIndex);
            final var unionTag = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionTag,
                    generateRandomStruct(null, false, unionData.fields, ctx));
        }
    }
}
