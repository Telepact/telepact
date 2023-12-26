package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class MockCallTypeExtension implements TypeExtension {

    public final Map<String, UType> types;

    public MockCallTypeExtension(Map<String, UType> types) {
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
                validationFailures
                        .add(new ValidationFailure("", "ExtensionValidationFailure",
                                Map.of("message", "StubMissingCall")));
            } else {
                var functionName = optionalFunctionName.get();
                var functionDef = (UFn) this.types.get(functionName);

                var input = (Map<String, Object>) givenMap.get(functionName);

                var inputFailures = functionDef.arg.validate(input, List.of(), List.of());
                var inputFailuresWithPath = inputFailures.stream()
                        .map(f -> new ValidationFailure(".%s%s".formatted(functionName, f.path), f.reason, f.data))
                        .toList();
                var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                        .filter(f -> !f.reason.equals("RequiredStructFieldMissing")).toList();

                validationFailures.addAll(inputFailuresWithoutMissingRequired);
            }

        } catch (ClassCastException e) {
            validationFailures.add(
                    new ValidationFailure("", "ExtensionValidationFailure", Map.of("message", "CallTypeRequired")));
        }

        return validationFailures;
    }

}
