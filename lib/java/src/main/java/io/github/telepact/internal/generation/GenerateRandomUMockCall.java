package io.github.telepact.internal.generation;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import io.github.telepact.internal.types.VFn;
import io.github.telepact.internal.types.VType;

public class GenerateRandomUMockCall {

    public static Object generateRandomUMockCall(Map<String, VType> types, GenerateContext ctx) {
        List<VFn> functions = types.entrySet().stream()
                .filter(entry -> entry.getValue() instanceof VFn)
                .filter(entry -> !entry.getKey().endsWith("_"))
                .map(entry -> (VFn) entry.getValue())
                .sorted((fn1, fn2) -> fn1.getName().compareTo(fn2.getName()))
                .collect(Collectors.toList());

        VFn selectedFn = functions.get(ctx.randomGenerator.nextIntWithCeiling(functions.size()));

        return GenerateRandomUnion.generateRandomUnion(null, false, selectedFn.call.tags,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
    }
}
