package uapi.internal.generation;

import java.util.*;
import java.util.stream.Collectors;
import uapi.internal.types.UFn;
import uapi.internal.types.UType;

import static uapi.internal.generation.GenerateRandomStruct.generateRandomStruct;

public class GenerateRandomUMockStub {

    public static Map<String, Object> generateRandomUMockStub(Map<String, UType> types, GenerateContext ctx) {
        List<UFn> functions = types.entrySet().stream()
                .filter(entry -> entry.getValue() instanceof UFn)
                .filter(entry -> !entry.getKey().endsWith("_"))
                .map(entry -> (UFn) entry.getValue())
                .sorted(Comparator.comparing(UFn::getName))
                .collect(Collectors.toList());

        int index = ctx.randomGenerator.nextIntWithCeiling(functions.size());

        System.out.println("index: " + index);

        UFn selectedFn = functions.get(index);

        System.out.println("selectedFn: " + selectedFn.name);

        var argFields = selectedFn.call.cases.get(selectedFn.name).fields;
        var okFields = selectedFn.result.cases.get("Ok_").fields;

        var arg = generateRandomStruct(argFields,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
        var okResult = generateRandomStruct(okFields,
                ctx.copyWithNewAlwaysIncludeRequiredFields(false));

        return Map.ofEntries(
                Map.entry(selectedFn.name, arg),
                Map.entry("->", Map.of("Ok_", okResult)));
    }
}
