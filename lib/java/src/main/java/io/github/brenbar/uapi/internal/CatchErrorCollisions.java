package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;

import static io.github.brenbar.uapi.internal.AsMap.asMap;

public class CatchErrorCollisions {
    static void catchErrorCollisions(List<Object> uApiSchemaPseudoJson, Set<Integer> errorIndices,
            Map<String, Integer> keysToIndex) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();

        final var indices = errorIndices.stream().sorted().toList();

        for (var i = 0; i < indices.size(); i += 1) {
            for (var j = i + 1; j < indices.size(); j += 1) {
                final var index = indices.get(i);
                final var otherIndex = indices.get(j);

                final var def = (Map<String, Object>) uApiSchemaPseudoJson.get(index);
                final var otherDef = (Map<String, Object>) uApiSchemaPseudoJson.get(otherIndex);

                final var errDef = (List<Object>) def.get("errors");
                final var otherErrDef = (List<Object>) otherDef.get("errors");

                for (int k = 0; k < errDef.size(); k += 1) {
                    final var thisErrDef = asMap(errDef.get(k));
                    final var thisErrDefKeys = new HashSet<>(thisErrDef.keySet());
                    thisErrDefKeys.remove("///");

                    for (int l = 0; l < otherErrDef.size(); l += 1) {
                        final var thisOtherErrDef = asMap(otherErrDef.get(l));
                        final var thisOtherErrDefKeys = new HashSet<>(thisOtherErrDef.keySet());
                        thisOtherErrDefKeys.remove("///");

                        if (thisErrDefKeys.equals(thisOtherErrDefKeys)) {
                            final var thisErrorDefKey = thisErrDefKeys.stream().findFirst().get();
                            final var thisOtherErrorDefKey = thisOtherErrDefKeys.stream().findFirst().get();
                            parseFailures.add(new SchemaParseFailure(
                                    List.of(otherIndex, "errors", l, thisOtherErrorDefKey), "PathCollision",
                                    Map.of("other", List.of(index, "errors", k, thisErrorDefKey)), "errors"));
                        }
                    }
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }
}
