package uapi.internal.generation;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import uapi.internal.types.UFn;
import uapi.internal.types.UType;

public class GenerateRandomUMockCall {

    public static Object generateRandomUMockCall(Map<String, UType> types, GenerateContext ctx) {
        List<UFn> functions = types.entrySet().stream()
                .filter(entry -> entry.getValue() instanceof UFn)
                .filter(entry -> !entry.getKey().endsWith("_"))
                .map(entry -> (UFn) entry.getValue())
                .sorted((fn1, fn2) -> fn1.getName().compareTo(fn2.getName()))
                .collect(Collectors.toList());

        UFn selectedFn = functions.get(ctx.randomGenerator.nextIntWithCeiling(functions.size()));

        return GenerateRandomUnion.generateRandomUnion(null, false, selectedFn.call.cases,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
    }
}
