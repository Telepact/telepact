package io.github.brenbar.uapi.internal.generation;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.RandomGenerator;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.UnionEntry.unionEntry;
import static io.github.brenbar.uapi.internal.generation.ConstructRandomStruct.constructRandomStruct;

public class ConstructRandomUnion {
    static Map<String, Object> constructRandomUnion(Map<String, UStruct> unionCasesReference,
            Map<String, Object> startingUnion,
            boolean includeOptionalFields, boolean randomizeOptionalFields,
            List<UTypeDeclaration> typeParameters,
            RandomGenerator randomGenerator) {
        if (!startingUnion.isEmpty()) {
            final var entry = unionEntry(startingUnion);
            final var unionCase = entry.getKey();
            final var unionStructType = unionCasesReference.get(unionCase);
            final var unionStartingStruct = (Map<String, Object>) startingUnion.get(unionCase);

            return Map.of(unionCase, constructRandomStruct(unionStructType.fields, unionStartingStruct,
                    includeOptionalFields, randomizeOptionalFields, typeParameters, randomGenerator));
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
                            typeParameters, randomGenerator));
        }
    }
}
