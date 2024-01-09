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
            givenMap = _CastUtil.asMap(givenObj);
        } catch (ClassCastException e) {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(new ArrayList<Object>(), givenObj, "Object");
        }

        var regexString = "^fn\\..*$";
        var optionalFunctionName = givenMap.keySet().stream().filter(k -> k.matches(regexString)).findAny();
        if (optionalFunctionName.isEmpty()) {
            return List.of(new ValidationFailure(new ArrayList<Object>(), "RequiredObjectKeyRegexMatchFailed",
                    Map.of("regex", regexString)));
        }
        var functionName = optionalFunctionName.get();
        var functionDef = (UFn) this.types.get(functionName);

        var input = givenMap.get(functionName);

        var inputFailures = functionDef.call.values.get(functionDef.name).validate(input, List.of(), List.of());
        var inputFailuresWithPath = inputFailures.stream()
                .map(f -> new ValidationFailure(_ValidateUtil.prepend(functionName, f.path), f.reason,
                        f.data))
                .toList();
        var inputFailuresWithoutMissingRequired = inputFailuresWithPath.stream()
                .filter(f -> !f.reason.equals("RequiredStructFieldMissing")).toList();

        validationFailures.addAll(inputFailuresWithoutMissingRequired);

        return validationFailures;
    }

}
