package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class _MockStubTypeExtension implements _UType {

    public final Map<String, _UType> types;

    public _MockStubTypeExtension(Map<String, _UType> types) {
        this.types = types;
    }

    @Override
    public List<ValidationFailure> validate(Object givenObj, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics) {
        var validationFailures = new ArrayList<ValidationFailure>();

        Map<String, Object> givenMap;
        try {
            givenMap = _CastUtil.asMap(givenObj);
        } catch (ClassCastException e) {
            return _ValidateUtil.getTypeUnexpectedValidationFailure(List.of(), givenObj, "Object");
        }

        var regexString = "^fn\\..*$";
        var matches = givenMap.keySet().stream().filter(k -> k.matches(regexString)).toList();
        if (matches.size() != 1) {
            return List.of(
                    new ValidationFailure(List.of(),
                            "ObjectKeyRegexMatchCountUnexpected",
                            Map.of("regex", regexString, "actual",
                                    matches.size(), "expected", 1)));

        }

        var functionName = matches.get(0);
        var functionDef = (_UFn) this.types.get(functionName);

        var input = givenMap.get(functionName);

        var inputFailures = functionDef.call.cases.get(functionDef.name).validate(input, List.of(),
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

    @Override
    public int getTypeParameterCount() {
        return 0;
    }

    @Override
    public Object generateRandomValue(Object startingValue, boolean useStartingValue,
            boolean includeRandomOptionalFields, List<_UTypeDeclaration> typeParameters,
            List<_UTypeDeclaration> generics, RandomGenerator random) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'generateRandomValue'");
    }

    @Override
    public String getName(List<_UTypeDeclaration> generics) {
        return "_ext._Stub";
    }

}
