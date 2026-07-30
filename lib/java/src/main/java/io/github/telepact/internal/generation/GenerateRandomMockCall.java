//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.generation;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TUnion;

public class GenerateRandomMockCall {

    public static Object generateRandomMockCall(Map<String, TType> types, GenerateContext ctx) {
        List<String> functionNames = types.keySet().stream()
                .filter(key -> key.startsWith("fn.") && !key.endsWith(".->"))
                .filter(key -> !key.endsWith("_"))
                .sorted((fn1, fn2) -> fn1.compareTo(fn2))
                .collect(Collectors.toList());

        String selectedFnName = functionNames.get(ctx.randomGenerator.nextIntWithCeiling(functionNames.size()));
        TUnion selectedFn = (TUnion) types.get(selectedFnName);

        return GenerateRandomUnion.generateRandomUnion(null, false, selectedFn.tags,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
    }
}
