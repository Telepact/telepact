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
        } catch (ClassCastException e) {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }

        var regexString = "^fn\\..*$";
        var optionalFunctionName = givenMap.keySet().stream().filter(k -> k.matches(regexString))
                .findAny();
        if (optionalFunctionName.isEmpty()) {
            return List.of(
                    new ValidationFailure(List.of(),
                            "RequiredObjectKeyRegexMatchFailed",
                            Map.of("regex", regexString)));

        }

        var functionName = optionalFunctionName.get();
        var functionDef = (UFn) this.types.get(functionName);

        var input = givenMap.get(functionName);

        var inputFailures = functionDef.call.values.get(functionDef.name).validate(input, List.of(),
                List.of());
        var inputFailuresWithPath = inputFailures.stream()
                .map(f -> new ValidationFailure(
                        _ValidateUtil.prepend(functionName, f.path),
                        f.reason,
                        f.data))
                .toList();

        var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !f.reason.equals("RequiredStructFieldMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        if (!givenMap.containsKey("->")) {
            return List.of(new ValidationFailure(List.of("->"),
                    "RequiredObjectKeyMissing",
                    Map.of()));
        }

        var output = givenMap.get("->");

        var outputFailures = functionDef.result.validate(output, List.of(), List.of());
        var outputFailuresWithPath = outputFailures.stream()
                .map(f -> new ValidationFailure(
                        _ValidateUtil.prepend("->", f.path), f.reason,
                        f.data))
                .toList();
        var failuresWithoutMissingRequired = outputFailuresWithPath
                .stream()
                .filter(f -> !f.reason.equals("RequiredStructFieldMissing"))
                .toList();

        validationFailures.addAll(failuresWithoutMissingRequired);

        return validationFailures;
    }

}
