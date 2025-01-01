package uapi.internal.generation;

import static uapi.internal.generation.ConstructRandomStruct.constructRandomStruct;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import uapi.RandomGenerator;
import uapi.internal.types.UStruct;

public class ConstructRandomUnion {
    static Map<String, Object> constructRandomUnion(Map<String, UStruct> unionCasesReference,
            Map<String, Object> startingUnion,
            boolean includeOptionalFields, boolean randomizeOptionalFields,
            RandomGenerator randomGenerator) {
        if (!startingUnion.isEmpty()) {
            final var entry = startingUnion.entrySet().stream().findAny().get();
            final var unionCase = entry.getKey();
            final var unionStructType = unionCasesReference.get(unionCase);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase, constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeOptionalFields, randomizeOptionalFields, randomGenerator));
        } else {
            final var sortedUnionCasesReference = new ArrayList<>(unionCasesReference.entrySet());

            Collections.sort(sortedUnionCasesReference, (e1, e2) -> e1.getKey().compareTo(e2.getKey()));

            final var randomIndex = randomGenerator.nextIntWithCeiling(sortedUnionCasesReference.size() - 1);
            final var unionEntry = sortedUnionCasesReference.get(randomIndex);
            final var unionCase = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionCase,
                    constructRandomStruct(unionData.fields, new HashMap<>(), includeOptionalFields,
                            randomizeOptionalFields,
                            randomGenerator));
        }
    }
}
