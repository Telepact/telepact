package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MockStubTypeExtension implements TypeExtension {

    public final Map<String, UType> types;

    public MockStubTypeExtension(Map<String, UType> types) {
        this.types = types;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj) {
        var validationFailures = new ArrayList<ValidationFailure>();

        Map<String, Object> givenMap;
        try {
            givenMap = (Map<String, Object>) givenObj;

            var optionalFunctionName = givenMap.keySet().stream().filter(k -> k.startsWith("fn.")).findAny();
            if (optionalFunctionName.isEmpty()) {
                validationFailures.add(new ValidationFailure("", "StubMissingCall"));

            } else {
                var functionName = optionalFunctionName.get();
                var functionDef = (UFn) this.types.get(functionName);

                var input = (Map<String, Object>) givenMap.get(functionName);

                var inputFailures = functionDef.arg.validate(input, List.of(), List.of());
                var inputFailuresWithPath = inputFailures.stream()
                        .map(f -> new ValidationFailure(".%s%s".formatted(functionName, f.path), f.reason))
                        .toList();

                var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                        .filter(f -> !f.reason.equals(_ValidateUtil.REQUIRED_STRUCT_FIELD_MISSING)).toList();

                validationFailures.addAll(inputFailuresWithoutMissingRequired);

                if (!givenMap.containsKey("->")) {
                    validationFailures.add(new ValidationFailure("", "StubMissingResult"));
                } else {

                    var output = (Map<String, Object>) givenMap.get("->");

                    var outputFailures = functionDef.result.validate(output, List.of(), List.of());
                    var outputFailuresWithPath = outputFailures.stream()
                            .map(f -> new ValidationFailure(".%s%s".formatted("->", f.path), f.reason)).toList();
                    var failuresWithoutMissingRequired = outputFailuresWithPath
                            .stream().filter(f -> !f.reason.equals(_ValidateUtil.REQUIRED_STRUCT_FIELD_MISSING))
                            .toList();

                    validationFailures.addAll(failuresWithoutMissingRequired);
                }
            }

        } catch (ClassCastException e) {
            validationFailures.add(new ValidationFailure("", "StubTypeRequired"));
        }

        return validationFailures;
    }

}
