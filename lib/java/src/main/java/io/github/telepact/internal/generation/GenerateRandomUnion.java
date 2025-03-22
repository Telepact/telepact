//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.generation;

import static io.github.telepact.internal.generation.GenerateRandomStruct.generateRandomStruct;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.TStruct;
import io.github.telepact.internal.types.TTypeDeclaration;

public class GenerateRandomUnion {
    public static Object generateRandomUnion(Object blueprintValue,
            boolean useBlueprintValue, Map<String, TStruct> unionTagsReference,
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

            final var randomIndex = ctx.randomGenerator.nextIntWithCeiling(sortedUnionTagsReference.size());
            final var unionEntry = sortedUnionTagsReference.get(randomIndex);
            final var unionTag = unionEntry.getKey();
            final var unionData = unionEntry.getValue();

            return Map.of(unionTag,
                    generateRandomStruct(null, false, unionData.fields, ctx));
        }
    }
}
