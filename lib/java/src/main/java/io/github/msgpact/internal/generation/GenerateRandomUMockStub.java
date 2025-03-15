package io.github.msgpact.internal.generation;

import static io.github.msgpact.internal.generation.GenerateRandomStruct.generateRandomStruct;

import java.util.*;
import java.util.stream.Collectors;

import io.github.msgpact.internal.types.VFn;
import io.github.msgpact.internal.types.VType;

public class GenerateRandomUMockStub {

        public static Map<String, Object> generateRandomUMockStub(Map<String, VType> types, GenerateContext ctx) {
                List<VFn> functions = types.entrySet().stream()
                                .filter(entry -> entry.getValue() instanceof VFn)
                                .filter(entry -> !entry.getKey().endsWith("_"))
                                .map(entry -> (VFn) entry.getValue())
                                .sorted(Comparator.comparing(VFn::getName))
                                .collect(Collectors.toList());

                int index = ctx.randomGenerator.nextIntWithCeiling(functions.size());

                System.out.println("index: " + index);

                VFn selectedFn = functions.get(index);

                System.out.println("selectedFn: " + selectedFn.name);

                var argFields = selectedFn.call.tags.get(selectedFn.name).fields;
                var okFields = selectedFn.result.tags.get("Ok_").fields;

                var arg = generateRandomStruct(null, false, argFields,
                                ctx.copyWithNewAlwaysIncludeRequiredFields(false));
                var okResult = generateRandomStruct(null, false, okFields,
                                ctx.copyWithNewAlwaysIncludeRequiredFields(false));

                return Map.ofEntries(
                                Map.entry(selectedFn.name, arg),
                                Map.entry("->", Map.of("Ok_", okResult)));
        }
}
